import re, pathlib

# ---- 1. Find the app's applicationId so we know where MainActivity.java lives ----
gradle_path = pathlib.Path("android/app/build.gradle")
gradle_text = gradle_path.read_text()
m = re.search(r'applicationId\s+"([\w.]+)"', gradle_text)
if not m:
    raise SystemExit("Could not find applicationId in android/app/build.gradle")
app_id = m.group(1)
package_dir = app_id.replace(".", "/")

java_root = pathlib.Path(f"android/app/src/main/java/{package_dir}")
main_activity_path = java_root / "MainActivity.java"
plugin_path = java_root / "AppLauncherPlugin.java"

if not main_activity_path.exists():
    raise SystemExit(f"MainActivity.java not found at {main_activity_path}")

# ---- 2. Write the native plugin ----
# Exposes one method, launch({ package: "com.hulu.plus" }), which starts the
# target app's own launch Intent -- the same call Android itself makes when
# you tap that app's icon on the home screen. If the app isn't installed,
# getLaunchIntentForPackage returns null and we resolve launched:false instead
# of crashing, so the caller can fall back to a web link.
plugin_java = f"""package {app_id};

import android.content.Intent;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "AppLauncher")
public class AppLauncherPlugin extends Plugin {{

    @PluginMethod
    public void launch(PluginCall call) {{
        String packageName = call.getString("package");
        if (packageName == null || packageName.isEmpty()) {{
            call.reject("No package name provided");
            return;
        }}

        Intent launchIntent = getContext().getPackageManager().getLaunchIntentForPackage(packageName);
        JSObject ret = new JSObject();

        if (launchIntent != null) {{
            launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            getContext().startActivity(launchIntent);
            ret.put("launched", true);
        }} else {{
            ret.put("launched", false);
        }}
        call.resolve(ret);
    }}
}}
"""
plugin_path.write_text(plugin_java)
print(f"Wrote {plugin_path}")

# ---- 3. Register the plugin in MainActivity.java ----
main_activity = main_activity_path.read_text()

if "AppLauncherPlugin" not in main_activity:
    # Add the registerPlugin(...) call inside onCreate, before super.onCreate(...)
    # -- this is Capacitor's documented pattern for bundling a plugin that lives
    # in the app itself rather than an npm package.
    main_activity = re.sub(
        r'(public class MainActivity extends BridgeActivity \{)',
        r'\1\n    {\n        registerPlugin(AppLauncherPlugin.class);\n    }',
        main_activity,
        count=1
    )
    main_activity_path.write_text(main_activity)
    print("Registered AppLauncherPlugin in MainActivity.java")
else:
    print("AppLauncherPlugin already registered, skipping.")

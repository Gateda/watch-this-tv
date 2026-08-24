import re, pathlib

p = pathlib.Path("android/app/src/main/AndroidManifest.xml")
xml = p.read_text()

if 'android:banner' not in xml:
    xml = re.sub(r'(<application\b)', r'\1 android:banner="@drawable/banner"', xml, count=1)

def add_orientation(m):
    tag = m.group(0)
    if 'android:screenOrientation' not in tag:
        tag = tag.replace('<activity', '<activity android:screenOrientation="landscape"', 1)
    return tag
xml = re.sub(r'<activity\b[^>]*>', add_orientation, xml, count=1)

if 'LEANBACK_LAUNCHER' not in xml:
    xml = xml.replace(
        '<category android:name="android.intent.category.LAUNCHER" />',
        '<category android:name="android.intent.category.LAUNCHER" />\n'
        '                <category android:name="android.intent.category.LEANBACK_LAUNCHER" />',
        1
    )

# Android 11+ (API 30+) hides other installed apps from getPackageManager() by
# default -- getLaunchIntentForPackage() silently returns null unless the
# package is explicitly declared here. This is what AppLauncherPlugin needs
# to actually see and launch Hulu (or any other service app added later).
# NOTE: <queries> must be a SIBLING of <application>, placed after it closes --
# not nested inside it, which is what caused the "found in <manifest><application>"
# AAPT error on the previous attempt.
if '<queries>' not in xml:
    queries_block = (
        '\n    <queries>\n'
        '        <package android:name="com.hulu.plus" />\n'
        '    </queries>'
    )
    xml = re.sub(r'(</application>)', r'\1' + queries_block, xml, count=1)

p.write_text(xml)
print("AndroidManifest.xml patched for Fire TV.")

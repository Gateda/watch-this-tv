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

p.write_text(xml)
print("AndroidManifest.xml patched for Fire TV.")

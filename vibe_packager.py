#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VibeToApk - One-Click Vibe Coding to Android APK Packager
Converts any HTML/CSS/JS AI-generated app into an Android Project & Cloud APK pipeline.
"""

import os
import sys
import shutil
import zipfile
import argparse
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def generate_android_manifest(app_name: str, package_name: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.VIBRATE" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="{app_name}"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.NoTitleBar.Fullscreen"
        android:hardwareAccelerated="true"
        android:usesCleartextTraffic="true">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|keyboardHidden|screenSize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""


def generate_main_activity(package_name: str) -> str:
    return f"""package {package_name};

import android.app.Activity;
import android.os.Bundle;
import android.view.KeyEvent;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;

public class MainActivity extends Activity {{
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setMediaPlaybackRequiresUserGesture(false);

        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient());

        // Load local asset web app
        webView.loadUrl("file:///android_asset/www/index.html");
    }}

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {{
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {{
            webView.goBack();
            return true;
        }}
        return super.onKeyDown(keyCode, event);
    }}
}}
"""


def generate_build_gradle(package_name: str = "com.vibecoding.app", version_code: int = 240, version_name: str = "2.4.0") -> str:
    return f"""plugins {{
    id 'com.android.application'
}}

android {{
    namespace '{package_name}'
    compileSdk 34

    defaultConfig {{
        applicationId "{package_name}"
        minSdk 21
        targetSdk 34
        versionCode {version_code}
        versionName "{version_name}"
    }}

    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
}}
"""


def generate_github_workflow(app_name: str) -> str:
    return f"""name: Build Vibe Coding APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Setup Android SDK
        uses: android-actions/setup-android@v3

      - name: Build APK with Gradle
        run: |
          chmod +x gradlew || true
          ./gradlew assembleDebug --stacktrace

      - name: Upload APK Artifact
        uses: actions/upload-artifact@v4
        with:
          name: {app_name}-Debug-APK
          path: app/build/outputs/apk/debug/*.apk
"""


def generate_pwa_files(app_name: str, target_dir: Path):
    manifest = {
        "name": app_name,
        "short_name": app_name,
        "start_url": "./index.html",
        "display": "standalone",
        "background_color": "#090d16",
        "theme_color": "#4f46e5",
        "orientation": "portrait",
        "icons": [
            {
                "src": "icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    import json
    (target_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    
    sw_code = """// Simple offline cache service worker
const CACHE_NAME = 'vibe-cache-v1';
self.addEventListener('install', (e) => {
  self.skipWaiting();
});
self.addEventListener('fetch', (e) => {
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
"""
    (target_dir / "sw.js").write_text(sw_code, encoding="utf-8")


def package_vibe_app(input_dir: Path, output_dir: Path, app_name: str = "VibeFocus", package_name: str = "com.vibecoding.vibefocus"):
    print("=" * 60)
    print(f"  VibeToApk Packager - [ {app_name} ]")
    print("=" * 60)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Prepare Android Project Structure
    app_dir = output_dir / "app"
    src_main = app_dir / "src" / "main"
    java_dir = src_main / "java" / package_name.replace(".", "/")
    assets_www = src_main / "assets" / "www"
    res_dir = src_main / "res"
    
    java_dir.mkdir(parents=True, exist_ok=True)
    assets_www.mkdir(parents=True, exist_ok=True)
    res_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy web assets into assets/www
    print(f"[1/4] Copying web assets from {input_dir.name} to assets/www...")
    if input_dir.is_file():
        shutil.copy2(input_dir, assets_www / "index.html")
    else:
        for item in input_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, assets_www / item.name)
            elif item.is_dir() and item.name != "output":
                shutil.copytree(item, assets_www / item.name, dirs_exist_ok=True)
                
    # Also add PWA manifest & sw only if missing so custom offline caches are preserved
    if not (assets_www / "manifest.json").exists() or not (assets_www / "sw.js").exists():
        generate_pwa_files(app_name, assets_www)
        print("      ✓ Injected fallback PWA manifest.json & sw.js")
    else:
        print("      ✓ Preserved custom PWA manifest.json & sw.js")

    # 2. Write Android Java & Manifest
    print(f"[2/4] Generating Android Native Java & Manifest...")
    (src_main / "AndroidManifest.xml").write_text(generate_android_manifest(app_name, package_name), encoding="utf-8")
    (java_dir / "MainActivity.java").write_text(generate_main_activity(package_name), encoding="utf-8")
    (app_dir / "build.gradle").write_text(generate_build_gradle(package_name, version_code=300, version_name="3.0.0"), encoding="utf-8")
    print("      ✓ AndroidManifest.xml (Hardware Accelerated, Fullscreen)")
    print(f"      ✓ MainActivity.java ({package_name})")

    # 3. Create Root Gradle & GitHub Action
    print(f"[3/4] Creating Build Pipeline & GitHub Actions...")
    (output_dir / "settings.gradle").write_text(f"rootProject.name = '{app_name}'\ninclude ':app'\n", encoding="utf-8")
    (output_dir / "build.gradle").write_text("""buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.2.2'
    }
}
allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
""", encoding="utf-8")
    
    workflows_dir = output_dir / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    (workflows_dir / "build-apk.yml").write_text(generate_github_workflow(app_name), encoding="utf-8")
    print("      ✓ .github/workflows/build-apk.yml (1-Click Cloud APK Build)")

    # 4. Create ZIP package
    print(f"[4/4] Creating ZIP package for distribution...")
    zip_path = output_dir.parent / f"{app_name}_Android_Project.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(output_dir)
                zf.write(full_path, rel_path)
    print(f"      ✓ Created ZIP: {zip_path.name} ({zip_path.stat().st_size / 1024:.1f} KB)")

    print("\n" + "=" * 60)
    print("SUCCESS! Your Vibe Coded App is packaged into a ready Android project.")
    print(f"Project folder: {output_dir.resolve()}")
    print(f"Ready ZIP:      {zip_path.resolve()}")
    print("=" * 60)
    return zip_path


def main():
    parser = argparse.ArgumentParser(description="VibeToApk Packager")
    parser.add_argument("-i", "--input", default="sample_vibe_app", help="Path to input web app folder or index.html")
    parser.add_argument("-o", "--output", default="generated_android_project", help="Output Android project directory")
    parser.add_argument("-n", "--name", default="VibeFocus", help="App Name")
    parser.add_argument("-p", "--package", default="com.vibecoding.vibefocus", help="Android Package Name")

    args = parser.parse_args()
    package_vibe_app(Path(args.input), Path(args.output), app_name=args.name, package_name=args.package)


if __name__ == "__main__":
    main()

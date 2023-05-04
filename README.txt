Requirements
1. Make sure that Android Emulator is running on local.
2. Make sure that python is installed.
3. Make sure that the APK file that you want to test is installed in the Emulator.

How to run auto-fuzzer
1. Run "pip install -r requirements.txt" (on first run)
2. Run "python ./main.py {package_name}" or "python ./main.py {path_to_apk}"
    examples:
        "python ./main.py com.example.myapplication"
        "python ./main.py /Desktop/target_app.apk"


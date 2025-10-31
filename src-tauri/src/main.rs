// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Command, Stdio};
use std::io::Write;
use std::path::PathBuf;
use serde_json;

// Helper function to get the Python executable path
fn get_python_executable() -> String {
    // Try environment variable first
    if let Ok(python_path) = std::env::var("PYTHON_EXECUTABLE") {
        if std::path::Path::new(&python_path).exists() {
            println!("Using Python from PYTHON_EXECUTABLE: {}", python_path);
            return python_path;
        }
    }

    // Try common venv paths in order
    if let Ok(home) = std::env::var("HOME") {
        let venv_paths = vec![
            format!("{}/.venv-py312/bin/python3", home),
            format!("{}/.venv/bin/python3", home),
            format!("{}/venv/bin/python3", home),
        ];

        for venv_path in venv_paths {
            if std::path::Path::new(&venv_path).exists() {
                println!("Using Python from venv: {}", venv_path);
                return venv_path;
            }
        }
    }

    // Fall back to system python3
    println!("Using system python3");
    "python3".to_string()
}

// Helper function to build LD_LIBRARY_PATH for CUDA/cuDNN support
fn get_ld_library_path() -> String {
    let mut existing_paths = Vec::new();

    // Check for cuDNN and CUDA libraries in common locations
    if let Ok(home) = std::env::var("HOME") {
        let cudnn_paths = vec![
            format!("{}/cudnn/lib", home),
            format!("{}/miniconda3/lib", home),
            format!("{}/anaconda3/lib", home),
        ];

        for cudnn_path in cudnn_paths {
            if std::path::Path::new(&cudnn_path).exists() {
                existing_paths.push(cudnn_path);
            }
        }
    }

    // Check system CUDA paths
    let system_paths = vec![
        "/usr/local/cuda/lib64",
        "/usr/local/cuda/lib",
    ];

    for sys_path in system_paths {
        if std::path::Path::new(sys_path).exists() {
            existing_paths.push(sys_path.to_string());
        }
    }

    let mut ld_library_path = existing_paths.join(":");

    // Append existing LD_LIBRARY_PATH if set
    if let Ok(existing) = std::env::var("LD_LIBRARY_PATH") {
        if !ld_library_path.is_empty() {
            ld_library_path.push(':');
        }
        ld_library_path.push_str(&existing);
    }

    ld_library_path
}

// Helper function to get the Python script path
fn get_python_script_path() -> PathBuf {
    // Try multiple approaches to find the Python script

    // Approach 1: Try Tauri's _up_ symlink (for production bundles)
    // In a bundled macOS app: Meeting Recap Processor.app/Contents/MacOS/meeting-recap-app
    // Resources are at: Meeting Recap Processor.app/Contents/Resources/_up_/src-python/
    if let Ok(exe_path) = std::env::current_exe() {
        if let Some(exe_dir) = exe_path.parent() {
            // From Contents/MacOS, go up to Contents, then check Resources/_up_
            if let Some(contents_dir) = exe_dir.parent() {
                let resources_path = contents_dir.join("Resources").join("_up_").join("src-python").join("main.py");
                if resources_path.exists() {
                    println!("Found Python script in app bundle Resources/_up_ at: {:?}", resources_path);
                    return resources_path;
                }

                // Also try directly in Resources
                let resources_path = contents_dir.join("Resources").join("src-python").join("main.py");
                if resources_path.exists() {
                    println!("Found Python script in app bundle Resources at: {:?}", resources_path);
                    return resources_path;
                }
            }

            // Alternative: try going up multiple levels from executable
            let mut test_path = exe_dir.to_path_buf();
            for _ in 0..8 {
                let script_path = test_path.join("src-python").join("main.py");
                if script_path.exists() {
                    println!("Found Python script at: {:?}", script_path);
                    return script_path;
                }
                if !test_path.pop() {
                    break;
                }
            }
        }
    }

    // Approach 2: Try relative to current directory (dev mode)
    let mut path = std::env::current_dir().unwrap();
    if path.ends_with("src-tauri") {
        path.pop(); // Go up to project root
    }
    path.push("src-python");
    path.push("main.py");

    println!("Python script path (fallback): {:?}", path);
    path
}

// Test Python connection
#[tauri::command]
fn test_python() -> Result<String, String> {
    // Try to run python with a simple test
    let python_exe = get_python_executable();
    let ld_library_path = get_ld_library_path();

    let output = Command::new(&python_exe)
        .arg("-c")
        .arg("import sys; print('Python ' + sys.version)")
        .env("LD_LIBRARY_PATH", ld_library_path)
        .output();

    match output {
        Ok(output) => {
            if output.status.success() {
                let version = String::from_utf8_lossy(&output.stdout);
                Ok(format!("Python bridge is working! {}", version.trim()))
            } else {
                let error = String::from_utf8_lossy(&output.stderr);
                Err(format!("Python execution failed: {}", error))
            }
        }
        Err(e) => Err(format!("Failed to run Python: {}", e)),
    }
}

// Call Python script for transcription
#[tauri::command]
async fn transcribe_audio(file_path: String, model: String, mode: Option<String>, whisper_host: Option<String>) -> Result<String, String> {
    let mode = mode.unwrap_or_else(|| "local".to_string());
    let whisper_host = whisper_host.unwrap_or_else(|| "http://192.168.68.10:9000".to_string());

    println!("Transcribing: {} with model: {} (mode: {})", file_path, model, mode);

    // Path to the Python script
    let python_script = get_python_script_path();

    // Create command JSON using serde_json for proper escaping
    let command = serde_json::json!({
        "command": "transcribe",
        "file": file_path,
        "model": model,
        "mode": mode,
        "whisper_host": whisper_host
    });
    let command = command.to_string();

    // Run Python script
    let python_exe = get_python_executable();
    let ld_library_path = get_ld_library_path();

    let mut child = Command::new(&python_exe)
        .arg(python_script)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .env("LD_LIBRARY_PATH", ld_library_path)
        .spawn()
        .map_err(|e| format!("Failed to start Python: {}", e))?;

    // Write command to stdin
    if let Some(mut stdin) = child.stdin.take() {
        stdin
            .write_all(command.as_bytes())
            .map_err(|e| format!("Failed to write to Python stdin: {}", e))?;
        stdin
            .write_all(b"\n")
            .map_err(|e| format!("Failed to write newline: {}", e))?;
    }

    // Wait for output
    let output = child
        .wait_with_output()
        .map_err(|e| format!("Failed to read Python output: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    // Always print debug output to console
    if !stderr.is_empty() {
        eprintln!("=== PYTHON STDERR ===\n{}\n=== END STDERR ===", stderr);
    }
    if !stdout.is_empty() {
        println!("=== PYTHON STDOUT ===\n{}\n=== END STDOUT ===", stdout);
    }

    if output.status.success() {
        // Parse JSON response
        if let Some(line) = stdout.lines().last() {
            if let Ok(json) = serde_json::from_str::<serde_json::Value>(line) {
                if json["status"] == "success" {
                    if let Some(path) = json["data"]["transcript_path"].as_str() {
                        return Ok(path.to_string());
                    }
                } else if json["status"] == "error" {
                    if let Some(error) = json["error"].as_str() {
                        return Err(error.to_string());
                    }
                }
            }
        }

        Err(format!("Unexpected Python output (last line): {}", stdout.lines().last().unwrap_or("(empty)")))
    } else {
        Err(format!("Python process failed with exit code: {:?}", output.status.code()))
    }
}

// Call Python script for analysis
#[tauri::command]
async fn analyze_transcript(file_path: String, ollama_host: Option<String>) -> Result<String, String> {
    let ollama_host = ollama_host.unwrap_or_else(|| "http://192.168.68.10:11434".to_string());
    println!("Analyzing transcript: {} with Ollama host: {}", file_path, ollama_host);

    let python_script = get_python_script_path();

    // Create command JSON using serde_json for proper escaping
    let command = serde_json::json!({
        "command": "analyze",
        "file": file_path,
        "ollama_host": ollama_host
    });
    let command = command.to_string();

    let python_exe = get_python_executable();
    let ld_library_path = get_ld_library_path();

    let mut child = Command::new(&python_exe)
        .arg(python_script)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .env("LD_LIBRARY_PATH", ld_library_path)
        .spawn()
        .map_err(|e| format!("Failed to start Python: {}", e))?;

    if let Some(mut stdin) = child.stdin.take() {
        stdin.write_all(command.as_bytes()).ok();
        stdin.write_all(b"\n").ok();
    }

    let output = child
        .wait_with_output()
        .map_err(|e| format!("Failed to read Python output: {}", e))?;

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);

        if let Some(line) = stdout.lines().last() {
            if let Ok(json) = serde_json::from_str::<serde_json::Value>(line) {
                if json["status"] == "success" {
                    if let Some(path) = json["data"]["analysis_path"].as_str() {
                        return Ok(path.to_string());
                    }
                }
            }
        }

        Err(format!("Analysis failed: {}", stdout))
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(format!("Python error: {}", stderr))
    }
}

// Call Python script for recap generation
#[tauri::command]
async fn generate_recap(file_path: String, style: String) -> Result<String, String> {
    println!("Generating recap from: {} with style: {}", file_path, style);

    let python_script = get_python_script_path();

    // Create command JSON using serde_json for proper escaping
    let command = serde_json::json!({
        "command": "recap",
        "file": file_path,
        "style": style
    });
    let command = command.to_string();

    let python_exe = get_python_executable();
    let ld_library_path = get_ld_library_path();

    let mut child = Command::new(&python_exe)
        .arg(python_script)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .env("LD_LIBRARY_PATH", ld_library_path)
        .spawn()
        .map_err(|e| format!("Failed to start Python: {}", e))?;

    if let Some(mut stdin) = child.stdin.take() {
        stdin.write_all(command.as_bytes()).ok();
        stdin.write_all(b"\n").ok();
    }

    let output = child
        .wait_with_output()
        .map_err(|e| format!("Failed to read Python output: {}", e))?;

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);

        if let Some(line) = stdout.lines().last() {
            if let Ok(json) = serde_json::from_str::<serde_json::Value>(line) {
                if json["status"] == "success" {
                    if let Some(text) = json["data"]["recap_path"].as_str() {
                        return Ok(text.to_string());
                    }
                }
            }
        }

        Err(format!("Recap generation failed: {}", stdout))
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(format!("Python error: {}", stderr))
    }
}

// Check health of remote Whisper server
#[tauri::command]
async fn check_whisper_health(whisper_host: String) -> Result<serde_json::Value, String> {
    let python_script = get_python_script_path();

    let command = serde_json::json!({
        "command": "check_whisper_health",
        "whisper_host": whisper_host
    });

    let python_exe = get_python_executable();
    let ld_library_path = get_ld_library_path();

    let mut child = Command::new(&python_exe)
        .arg(python_script)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .env("LD_LIBRARY_PATH", ld_library_path)
        .spawn()
        .map_err(|e| format!("Failed to start Python: {}", e))?;

    if let Some(mut stdin) = child.stdin.take() {
        stdin.write_all(command.to_string().as_bytes()).ok();
        stdin.write_all(b"\n").ok();
    }

    let output = child
        .wait_with_output()
        .map_err(|e| format!("Failed to read Python output: {}", e))?;

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        if let Some(line) = stdout.lines().last() {
            if let Ok(json) = serde_json::from_str::<serde_json::Value>(line) {
                // Extract data field from response
                if let Some(data) = json.get("data") {
                    return Ok(data.clone());
                }
                return Ok(json);
            }
        }
        Err("No valid response from Python".to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(format!("Python error: {}", stderr))
    }
}

// Check health of remote Ollama server
#[tauri::command]
async fn check_ollama_health(ollama_host: String) -> Result<serde_json::Value, String> {
    let python_script = get_python_script_path();

    let command = serde_json::json!({
        "command": "check_ollama_health",
        "ollama_host": ollama_host
    });

    let python_exe = get_python_executable();
    let ld_library_path = get_ld_library_path();

    let mut child = Command::new(&python_exe)
        .arg(python_script)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .env("LD_LIBRARY_PATH", ld_library_path)
        .spawn()
        .map_err(|e| format!("Failed to start Python: {}", e))?;

    if let Some(mut stdin) = child.stdin.take() {
        stdin.write_all(command.to_string().as_bytes()).ok();
        stdin.write_all(b"\n").ok();
    }

    let output = child
        .wait_with_output()
        .map_err(|e| format!("Failed to read Python output: {}", e))?;

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        if let Some(line) = stdout.lines().last() {
            if let Ok(json) = serde_json::from_str::<serde_json::Value>(line) {
                // Extract data field from response
                if let Some(data) = json.get("data") {
                    return Ok(data.clone());
                }
                return Ok(json);
            }
        }
        Err("No valid response from Python".to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(format!("Python error: {}", stderr))
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![
            test_python,
            transcribe_audio,
            analyze_transcript,
            generate_recap,
            check_whisper_health,
            check_ollama_health
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from pathlib import Path
import logging
import datetime
import json
import threading
import queue
from PIL import Image, ImageTk, ImageDraw, ImageFont
import hashlib
import shutil
import math
import sys
import platform
import webbrowser
from tkinter import font as tkfont

# ------------------- Configuration Manager -------------------
class ConfigManager:
    CONFIG_FILE = "apk_signer_config.json"
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        default_config = {
            "JDK_PATH": self._find_jdk_path(),
            "SDK_BUILD_TOOLS": self._find_sdk_path(),
            "KEYSTORE": "",
            "STOREPASS": "",
            "KEYPASS": "",
            "ALIAS": "",
            "OUTPUT_DIR": str(Path.home() / "Signed_APKs"),
            "LOG_LEVEL": "INFO",
            "THEME": "dark",
            "WINDOW_GEOMETRY": "1000x750",
            "AUTO_OPEN_OUTPUT": True,
            "COPY_TO_CLIPBOARD": True
        }
        
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**default_config, **loaded_config}
        except Exception as e:
            print(f"Error loading config: {e}")
        
        return default_config
    
    def _find_jdk_path(self):
        """Try to find JDK path automatically"""
        common_paths = [
            r"C:\Program Files\Java\jdk-17.0.2",
            r"C:\Program Files\Java\jdk-11.0.12",
            r"C:\Program Files\Java\jdk-1.8",
            r"C:\Program Files\Java\jdk-21"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        # Try to find in PATH
        try:
            result = subprocess.run(["where", "java"], capture_output=True, text=True)
            if result.returncode == 0:
                java_path = result.stdout.split('\n')[0].strip()
                jdk_path = str(Path(java_path).parent.parent)
                if os.path.exists(jdk_path):
                    return jdk_path
        except:
            pass
        
        return r"C:\Program Files\Java\jdk-17.0.2"
    
    def _find_sdk_path(self):
        """Try to find Android SDK path automatically"""
        common_paths = [
            r"C:\Android\Sdk\build-tools\34.0.0",
            r"C:\Android\Sdk\build-tools\33.0.1",
            r"C:\Android\Sdk\build-tools\33.0.0",
            r"C:\Android\Sdk\build-tools\30.0.3"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        # Try to find ANDROID_HOME environment variable
        android_home = os.environ.get('ANDROID_HOME')
        if android_home:
            build_tools_path = os.path.join(android_home, "build-tools")
            if os.path.exists(build_tools_path):
                # Find the latest version
                versions = [d for d in os.listdir(build_tools_path) if os.path.isdir(os.path.join(build_tools_path, d))]
                if versions:
                    versions.sort(reverse=True)
                    return os.path.join(build_tools_path, versions[0])
        
        return r"C:\Android\Sdk\build-tools\34.0.0"
    
    def save_config(self):
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()

# ------------------- Theme Manager -------------------
class ThemeManager:
    def __init__(self):
        self.themes = {
            "dark": {
                "bg": "#1e1e1e",
                "fg": "#ffffff",
                "accent": "#4a90e2",
                "accent_hover": "#5ba0f2",
                "accent_active": "#3a7bc8",
                "secondary": "#2d2d30",
                "tertiary": "#3e3e42",
                "border": "#3e3e42",
                "success": "#4caf50",
                "warning": "#ff9800",
                "error": "#f44336",
                "font": "Segoe UI",
                "font_size": 10,
                "title_font": "Segoe UI",
                "title_font_size": 18,
                "subtitle_font": "Segoe UI",
                "subtitle_font_size": 12
            },
            "light": {
                "bg": "#f5f5f5",
                "fg": "#333333",
                "accent": "#4a90e2",
                "accent_hover": "#5ba0f2",
                "accent_active": "#3a7bc8",
                "secondary": "#ffffff",
                "tertiary": "#e0e0e0",
                "border": "#cccccc",
                "success": "#4caf50",
                "warning": "#ff9800",
                "error": "#f44336",
                "font": "Segoe UI",
                "font_size": 10,
                "title_font": "Segoe UI",
                "title_font_size": 18,
                "subtitle_font": "Segoe UI",
                "subtitle_font_size": 12
            },
            "blue": {
                "bg": "#0d47a1",
                "fg": "#ffffff",
                "accent": "#64b5f6",
                "accent_hover": "#90caf9",
                "accent_active": "#42a5f5",
                "secondary": "#1565c0",
                "tertiary": "#1976d2",
                "border": "#1e88e5",
                "success": "#81c784",
                "warning": "#ffb74d",
                "error": "#e57373",
                "font": "Segoe UI",
                "font_size": 10,
                "title_font": "Segoe UI",
                "title_font_size": 18,
                "subtitle_font": "Segoe UI",
                "subtitle_font_size": 12
            },
            "green": {
                "bg": "#1b5e20",
                "fg": "#ffffff",
                "accent": "#81c784",
                "accent_hover": "#a5d6a7",
                "accent_active": "#66bb6a",
                "secondary": "#2e7d32",
                "tertiary": "#388e3c",
                "border": "#43a047",
                "success": "#a5d6a7",
                "warning": "#ffb74d",
                "error": "#e57373",
                "font": "Segoe UI",
                "font_size": 10,
                "title_font": "Segoe UI",
                "title_font_size": 18,
                "subtitle_font": "Segoe UI",
                "subtitle_font_size": 12
            },
            "purple": {
                "bg": "#4a148c",
                "fg": "#ffffff",
                "accent": "#ba68c8",
                "accent_hover": "#ce93d8",
                "accent_active": "#ab47bc",
                "secondary": "#6a1b9a",
                "tertiary": "#7b1fa2",
                "border": "#8e24aa",
                "success": "#a5d6a7",
                "warning": "#ffb74d",
                "error": "#e57373",
                "font": "Segoe UI",
                "font_size": 10,
                "title_font": "Segoe UI",
                "title_font_size": 18,
                "subtitle_font": "Segoe UI",
                "subtitle_font_size": 12
            }
        }
    
    def get_theme(self, theme_name):
        return self.themes.get(theme_name, self.themes["dark"])
    
    def get_available_themes(self):
        return list(self.themes.keys())

# ------------------- Icon Generator -------------------
class IconGenerator:
    @staticmethod
    def create_icon(size, color, icon_type):
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center = size // 2
        padding = size // 5
        
        if icon_type == "folder":
            # Folder icon
            draw.rectangle([padding, padding + size//4, size - padding, size - padding], fill=color)
            draw.rectangle([padding, padding, size - padding, padding + size//3], fill=color)
            
        elif icon_type == "apk":
            # APK icon
            draw.rectangle([padding, padding, size - padding, size - padding], fill=color, outline=color, width=2)
            draw.text((center, center), "APK", fill=(255, 255, 255, 255), anchor="mm")
            
        elif icon_type == "settings":
            # Settings gear icon
            outer_radius = size // 2 - padding
            inner_radius = outer_radius // 2
            teeth = 8
            tooth_angle = 360 / teeth
            
            for i in range(teeth):
                angle1 = math.radians(i * tooth_angle)
                angle2 = math.radians((i + 0.5) * tooth_angle)
                angle3 = math.radians((i + 1) * tooth_angle)
                
                x1 = center + outer_radius * math.cos(angle1)
                y1 = center + outer_radius * math.sin(angle1)
                x2 = center + (outer_radius + padding//2) * math.cos(angle2)
                y2 = center + (outer_radius + padding//2) * math.sin(angle2)
                x3 = center + outer_radius * math.cos(angle3)
                y3 = center + outer_radius * math.sin(angle3)
                
                draw.polygon([(center, center), (x1, y1), (x2, y2), (x3, y3)], fill=color)
            
            draw.ellipse([center - inner_radius, center - inner_radius, 
                          center + inner_radius, center + inner_radius], fill=(0, 0, 0, 0))
            
        elif icon_type == "history":
            # History clock icon
            draw.ellipse([padding, padding, size - padding, size - padding], outline=color, width=2)
            # Clock hands
            draw.line([center, center, center, center - size//3], fill=color, width=2)
            draw.line([center, center, center + size//4, center], fill=color, width=2)
            
        elif icon_type == "log":
            # Log document icon
            draw.rectangle([padding, padding, size - padding, size - padding], fill=color)
            # Lines
            line_spacing = size // 6
            for i in range(3):
                y = padding + line_spacing * (i + 1)
                draw.line([padding + size//4, y, size - padding - size//4, y], fill=(255, 255, 255, 255), width=1)
            
        elif icon_type == "sign":
            # Pen/Signature icon
            draw.line([padding, size - padding, size - padding, padding], fill=color, width=3)
            # Pen tip
            draw.polygon([(size - padding - 5, padding), (size - padding, padding), 
                         (size - padding, padding + 5)], fill=color)
            
        elif icon_type == "batch":
            # Multiple files icon
            for i in range(3):
                offset = i * 3
                draw.rectangle([padding + offset, padding + offset, 
                               size - padding + offset, size - padding + offset], 
                              fill=color, outline=color)
            
        elif icon_type == "refresh":
            # Refresh icon
            draw.arc([padding, padding, size - padding, size - padding], start=0, end=270, fill=color, width=3)
            # Arrow
            draw.polygon([(size - padding - 5, padding + 5), 
                         (size - padding, padding), 
                         (size - padding, padding + 10)], fill=color)
            
        elif icon_type == "clear":
            # X icon
            draw.line([padding, padding, size - padding, size - padding], fill=color, width=3)
            draw.line([size - padding, padding, padding, size - padding], fill=color, width=3)
            
        elif icon_type == "save":
            # Save icon
            draw.rectangle([padding, padding, size - padding, size - padding], fill=color)
            draw.polygon([(center, padding + size//4), 
                         (padding + size//4, padding + size//2), 
                         (size - padding - size//4, padding + size//2)], fill=(0, 0, 0, 0))
            draw.rectangle([padding + size//4, padding + size//2, 
                           size - padding - size//4, size - padding], fill=(0, 0, 0, 0))
            
        elif icon_type == "export":
            # Export icon
            draw.rectangle([padding, padding, size - padding, size - padding], fill=color)
            # Arrow pointing right
            draw.polygon([(size - padding - size//4, center), 
                         (size - padding, center - size//8), 
                         (size - padding, center + size//8)], fill=(255, 255, 255, 255))
            
        elif icon_type == "verify":
            # Checkmark icon
            draw.ellipse([padding, padding, size - padding, size - padding], outline=color, width=2)
            # Checkmark
            draw.line([size//3, center, center - size//8, center + size//4], fill=color, width=3)
            draw.line([center - size//8, center + size//4, size*2//3, center - size//4], fill=color, width=3)
            
        elif icon_type == "info":
            # Info icon
            draw.ellipse([padding, padding, size - padding, size - padding], fill=color)
            draw.text((center, center - size//8), "i", fill=(255, 255, 255, 255), anchor="mm", font=ImageFont.truetype("arial.ttf", size//2))
            
        elif icon_type == "open":
            # Open folder icon
            draw.rectangle([padding, padding + size//4, size - padding, size - padding], fill=color)
            draw.rectangle([padding, padding, size - padding, padding + size//3], fill=color)
            # Arrow pointing out
            draw.polygon([(size - padding - size//4, center), 
                         (size - padding, center - size//8), 
                         (size - padding, center + size//8)], fill=(255, 255, 255, 255))
            
        elif icon_type == "copy":
            # Copy icon
            draw.rectangle([padding, padding, size - padding - size//4, size - padding - size//4], fill=color)
            draw.rectangle([padding + size//4, padding + size//4, size - padding, size - padding], fill=color)
            
        return ImageTk.PhotoImage(img)

# ------------------- Advanced APK Signer -------------------
class AdvancedApkSigner:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.setup_logging()
        self.history = self.load_history()
    
    def setup_logging(self):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"apk_signer_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Get log level with default
        log_level_name = self.config_manager.get("LOG_LEVEL", "INFO")
        log_level = getattr(logging, log_level_name, logging.INFO)
        
        logging.basicConfig(
            filename=log_file,
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add console handler
        console = logging.StreamHandler()
        console.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger().addHandler(console)
        
        logging.info(f"APK Signer started. Log file: {log_file}")
    
    def load_history(self):
        history_file = Path("signing_history.json")
        try:
            if history_file.exists():
                with open(history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading history: {e}")
        return []
    
    def save_history(self):
        history_file = Path("signing_history.json")
        try:
            with open(history_file, 'w') as f:
                json.dump(self.history[-50:], f, indent=4)  # Keep last 50 entries
        except Exception as e:
            logging.error(f"Error saving history: {e}")
    
    def run_cmd(self, cmd, step_name, progress_queue=None):
        logging.info(f"Step: {step_name} | Command: {' '.join(cmd)}")
        if progress_queue:
            progress_queue.put(("log", f"Running: {' '.join(cmd)}"))
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                shell=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip()
                logging.error(f"Error in {step_name}: {error_msg}")
                if progress_queue:
                    progress_queue.put(("error", error_msg))
                raise RuntimeError(error_msg)
            
            output = result.stdout.strip()
            logging.info(f"Output: {output}")
            if progress_queue:
                progress_queue.put(("log", output))
            return output
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout in {step_name}"
            logging.error(error_msg)
            if progress_queue:
                progress_queue.put(("error", error_msg))
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Exception in {step_name}: {str(e)}"
            logging.error(error_msg)
            if progress_queue:
                progress_queue.put(("error", error_msg))
            raise
    
    def verify_tools(self):
        tools = {
            "jarsigner": os.path.join(self.config_manager.get("JDK_PATH"), "bin", "jarsigner.exe"),
            "zipalign": os.path.join(self.config_manager.get("SDK_BUILD_TOOLS"), "zipalign.exe"),
            "apksigner": os.path.join(self.config_manager.get("SDK_BUILD_TOOLS"), "apksigner.bat")
        }
        
        missing = []
        for name, path in tools.items():
            if not os.path.exists(path):
                missing.append(f"{name}: {path}")
        
        if missing:
            raise RuntimeError(f"Missing required tools:\n" + "\n".join(missing))
        
        return tools
    
    def sign_apk(self, apk_path, progress_queue=None):
        try:
            tools = self.verify_tools()
            apk_path = str(Path(apk_path).resolve())
            
            # Create output directory if not exists
            output_dir = Path(self.config_manager.get("OUTPUT_DIR"))
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate output filename
            apk_name = Path(apk_path).stem
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{apk_name}_signed_{timestamp}.apk"
            output_path = output_dir / output_name
            
            # Calculate original APK hash
            original_hash = self.calculate_hash(apk_path)
            
            steps = [
                ("Jarsigner Signing", [
                    tools["jarsigner"], "-verbose", "-sigalg", "SHA256withRSA", 
                    "-digestalg", "SHA-256", "-keystore", self.config_manager.get("KEYSTORE"), 
                    "-storepass", self.config_manager.get("STOREPASS"), 
                    "-keypass", self.config_manager.get("KEYPASS"), apk_path, 
                    self.config_manager.get("ALIAS")
                ]),
                ("Zipalign APK", [
                    tools["zipalign"], "-v", "-p", "4", apk_path, str(output_path)
                ]),
                ("Apksigner Signing", [
                    tools["apksigner"], "sign", "--ks", self.config_manager.get("KEYSTORE"), 
                    f"--ks-pass=pass:{self.config_manager.get('STOREPASS')}", 
                    f"--key-pass=pass:{self.config_manager.get('KEYPASS')}", 
                    "--ks-key-alias", self.config_manager.get("ALIAS"), str(output_path)
                ]),
                ("Verify APK", [
                    tools["apksigner"], "verify", str(output_path)
                ])
            ]
            
            for i, (step_name, cmd) in enumerate(steps, 1):
                if progress_queue:
                    progress_queue.put(("progress", i / len(steps), step_name))
                self.run_cmd(cmd, step_name, progress_queue)
            
            # Calculate signed APK hash
            signed_hash = self.calculate_hash(str(output_path))
            
            # Add to history
            history_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "original_apk": apk_path,
                "signed_apk": str(output_path),
                "original_hash": original_hash,
                "signed_hash": signed_hash,
                "status": "success"
            }
            self.history.append(history_entry)
            self.save_history()
            
            if progress_queue:
                progress_queue.put(("complete", str(output_path)))
            
            return str(output_path)
        
        except Exception as e:
            if progress_queue:
                progress_queue.put(("failed", str(e)))
            raise
    
    def calculate_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def batch_sign(self, apk_paths, progress_queue=None):
        results = []
        total = len(apk_paths)
        
        for i, apk_path in enumerate(apk_paths, 1):
            try:
                if progress_queue:
                    progress_queue.put(("batch_progress", i / total, f"Processing {Path(apk_path).name}"))
                
                result = self.sign_apk(apk_path, progress_queue)
                results.append({"path": apk_path, "result": result, "status": "success"})
            except Exception as e:
                results.append({"path": apk_path, "result": str(e), "status": "failed"})
        
        if progress_queue:
            progress_queue.put(("batch_complete", results))
        
        return results
    
    def verify_apk(self, apk_path, progress_queue=None):
        try:
            tools = self.verify_tools()
            apk_path = str(Path(apk_path).resolve())
            
            if progress_queue:
                progress_queue.put(("log", f"Verifying APK: {apk_path}"))
            
            # Verify APK signature
            cmd = [tools["apksigner"], "verify", apk_path]
            self.run_cmd(cmd, "Verify APK", progress_queue)
            
            # Get APK info
            cmd = [tools["apksigner"], "verify", "--print-certs", apk_path]
            output = self.run_cmd(cmd, "Get APK Info", progress_queue)
            
            if progress_queue:
                progress_queue.put(("verify_complete", output))
            
            return True
        except Exception as e:
            if progress_queue:
                progress_queue.put(("verify_failed", str(e)))
            return False

# ------------------- Professional GUI -------------------
class ApkSignerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("APK Super Signer Pro")
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.theme_manager = ThemeManager()
        self.signer = AdvancedApkSigner(self.config_manager)
        self.progress_queue = queue.Queue()
        self.current_theme = self.config_manager.get("THEME")
        self.theme = self.theme_manager.get_theme(self.current_theme)
        
        # Set window geometry
        geometry = self.config_manager.get("WINDOW_GEOMETRY", "1000x750")
        self.root.geometry(geometry)
        self.root.minsize(900, 650)
        
        # Create main container first
        self.main_container = tk.Frame(self.root, bg=self.theme["bg"])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Set theme after creating main container
        self.set_theme(self.current_theme)
        
        # Create header
        self.create_header()
        
        # Create main notebook
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create tabs
        self.create_signing_tab()
        self.create_batch_tab()
        self.create_verify_tab()
        self.create_history_tab()
        self.create_settings_tab()
        self.create_log_tab()
        self.create_about_tab()
        
        # Create footer
        self.create_footer()
        
        # Start progress monitor
        self.root.after(100, self.process_progress_queue)
        
        # Set window icon (if available)
        self.set_window_icon()
        
        # Center window
        self.center_window()
        
        # Setup drag and drop (fallback implementation)
        self.setup_drag_drop_fallback()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Save window geometry on resize
        self.root.bind("<Configure>", self.on_window_resize)
    
    def set_theme(self, theme_name):
        self.current_theme = theme_name
        self.theme = self.theme_manager.get_theme(theme_name)
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure common styles
        style.configure("TFrame", background=self.theme["bg"])
        style.configure("TLabel", background=self.theme["bg"], foreground=self.theme["fg"], 
                        font=(self.theme["font"], self.theme["font_size"]))
        style.configure("TButton", background=self.theme["accent"], foreground=self.theme["fg"],
                        font=(self.theme["font"], self.theme["font_size"], "bold"),
                        padding=6, relief="flat", borderwidth=0)
        style.map("TButton", 
                 background=[('active', self.theme["accent_active"]), 
                            ('!disabled', self.theme["accent"])],
                 foreground=[('active', self.theme["fg"]), 
                            ('!disabled', self.theme["fg"])])
        
        style.configure("Accent.TButton", background=self.theme["accent"], 
                        foreground=self.theme["fg"],
                        font=(self.theme["font"], self.theme["font_size"], "bold"),
                        padding=8, relief="flat", borderwidth=0)
        style.map("Accent.TButton", 
                 background=[('active', self.theme["accent_active"]), 
                            ('!disabled', self.theme["accent"])],
                 foreground=[('active', self.theme["fg"]), 
                            ('!disabled', self.theme["fg"])])
        
        style.configure("TEntry", fieldbackground=self.theme["secondary"], 
                        foreground=self.theme["fg"],
                        borderwidth=1, relief="solid",
                        font=(self.theme["font"], self.theme["font_size"]))
        style.map("TEntry", 
                 bordercolor=[('focus', self.theme["accent"])],
                 lightcolor=[('focus', self.theme["accent"])],
                 darkcolor=[('focus', self.theme["accent"])])
        
        style.configure("TProgressbar", background=self.theme["accent"], 
                        troughcolor=self.theme["tertiary"],
                        borderwidth=0, relief="flat")
        
        style.configure("TNotebook", background=self.theme["bg"], 
                        borderwidth=0, tabmargins=0)
        style.configure("TNotebook.Tab", background=self.theme["tertiary"], 
                        foreground=self.theme["fg"],
                        padding=[12, 8], borderwidth=0,
                        font=(self.theme["font"], self.theme["font_size"]))
        style.map("TNotebook.Tab", 
                 background=[('selected', self.theme["accent"]), 
                            ('active', self.theme["secondary"])],
                 foreground=[('selected', self.theme["fg"]), 
                            ('active', self.theme["fg"])])
        
        style.configure("Treeview", background=self.theme["secondary"], 
                        foreground=self.theme["fg"],
                        fieldbackground=self.theme["secondary"],
                        borderwidth=0, font=(self.theme["font"], self.theme["font_size"]))
        style.configure("Treeview.Heading", background=self.theme["tertiary"], 
                        foreground=self.theme["fg"],
                        borderwidth=0, font=(self.theme["font"], self.theme["font_size"], "bold"))
        style.map("Treeview", 
                 background=[('selected', self.theme["accent"])],
                 foreground=[('selected', self.theme["fg"])])
        
        style.configure("TScrollbar", background=self.theme["tertiary"], 
                        troughcolor=self.theme["bg"],
                        borderwidth=0, width=10)
        style.map("TScrollbar", 
                 background=[('active', self.theme["accent"])])
        
        style.configure("TCombobox", fieldbackground=self.theme["secondary"], 
                        background=self.theme["secondary"],
                        foreground=self.theme["fg"],
                        borderwidth=1, relief="solid",
                        font=(self.theme["font"], self.theme["font_size"]),
                        padding=4)
        style.map("TCombobox", 
                 bordercolor=[('focus', self.theme["accent"])],
                 lightcolor=[('focus', self.theme["accent"])],
                 darkcolor=[('focus', self.theme["accent"])])
        
        style.configure("TLabelFrame", background=self.theme["bg"], 
                        foreground=self.theme["fg"],
                        borderwidth=1, relief="solid",
                        bordercolor=self.theme["border"],
                        font=(self.theme["font"], self.theme["font_size"], "bold"))
        style.configure("TLabelFrame.Label", background=self.theme["bg"], 
                        foreground=self.theme["fg"],
                        font=(self.theme["font"], self.theme["font_size"], "bold"))
        
        style.configure("Horizontal.TProgressbar", background=self.theme["accent"], 
                        troughcolor=self.theme["tertiary"],
                        borderwidth=0, relief="flat")
        
        # Update main container and root background
        self.main_container.config(bg=self.theme["bg"])
        self.root.config(bg=self.theme["bg"])
        
        # Update all child widgets
        for widget in self.main_container.winfo_children():
            self.update_widget_theme(widget)
    
    def update_widget_theme(self, widget):
        try:
            widget_class = widget.winfo_class()
            
            if widget_class == "Frame":
                widget.config(bg=self.theme["bg"])
            elif widget_class == "Label":
                widget.config(bg=self.theme["bg"], fg=self.theme["fg"])
            elif widget_class == "Button":
                widget.config(bg=self.theme["accent"], fg=self.theme["fg"],
                             activebackground=self.theme["accent_active"],
                             font=(self.theme["font"], self.theme["font_size"], "bold"))
            elif widget_class == "Entry":
                widget.config(bg=self.theme["secondary"], fg=self.theme["fg"],
                             insertbackground=self.theme["fg"],
                             font=(self.theme["font"], self.theme["font_size"]))
            elif widget_class == "Text":
                widget.config(bg=self.theme["secondary"], fg=self.theme["fg"],
                             insertbackground=self.theme["fg"],
                             font=(self.theme["font"], self.theme["font_size"]))
            elif widget_class == "Listbox":
                widget.config(bg=self.theme["secondary"], fg=self.theme["fg"],
                             selectbackground=self.theme["accent"],
                             font=(self.theme["font"], self.theme["font_size"]))
            elif widget_class == "Canvas":
                widget.config(bg=self.theme["bg"])
            elif widget_class == "Scale":
                widget.config(bg=self.theme["bg"], fg=self.theme["fg"],
                             troughcolor=self.theme["tertiary"],
                             activebackground=self.theme["accent"],
                             font=(self.theme["font"], self.theme["font_size"]))
            
            # Recursively update child widgets
            for child in widget.winfo_children():
                self.update_widget_theme(child)
        except:
            pass  # Skip widgets that don't support these options
    
    def create_header(self):
        header_frame = tk.Frame(self.main_container, bg=self.theme["secondary"], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Logo and title
        logo_frame = tk.Frame(header_frame, bg=self.theme["secondary"])
        logo_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Create a canvas for the logo
        logo_canvas = tk.Canvas(logo_frame, width=60, height=60, bg=self.theme["secondary"], highlightthickness=0)
        logo_canvas.pack(side=tk.LEFT, padx=(0, 10))
        
        # Draw APK icon on canvas
        self.draw_apk_icon(logo_canvas, 60, self.theme["accent"])
        
        # Title
        title_label = tk.Label(
            logo_frame, 
            text="APK Super Signer Pro", 
            font=(self.theme["title_font"], self.theme["title_font_size"], "bold"),
            bg=self.theme["secondary"],
            fg=self.theme["fg"]
        )
        title_label.pack(side=tk.LEFT, pady=15)
        
        # Subtitle
        subtitle_label = tk.Label(
            logo_frame, 
            text="Professional Android APK Signing Tool", 
            font=(self.theme["subtitle_font"], self.theme["subtitle_font_size"]),
            bg=self.theme["secondary"],
            fg=self.theme["fg"]
        )
        subtitle_label.pack(side=tk.LEFT, pady=(0, 15))
        
        # Theme selector
        theme_frame = tk.Frame(header_frame, bg=self.theme["secondary"])
        theme_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        theme_label = tk.Label(
            theme_frame, 
            text="Theme:", 
            font=(self.theme["font"], self.theme["font_size"]),
            bg=self.theme["secondary"],
            fg=self.theme["fg"]
        )
        theme_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(
            theme_frame, 
            textvariable=self.theme_var, 
            values=self.theme_manager.get_available_themes(),
            state="readonly",
            width=10
        )
        theme_combo.pack(side=tk.LEFT)
        theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
    
    def draw_apk_icon(self, canvas, size, color):
        # Draw a stylized APK icon
        center = size // 2
        padding = size // 5
        
        # Draw outer rectangle
        canvas.create_rectangle(
            padding, padding, 
            size - padding, size - padding,
            fill=color, outline=""
        )
        
        # Draw inner triangle
        canvas.create_polygon(
            center, padding + 5,
            size - padding - 5, size - padding - 5,
            padding + 5, size - padding - 5,
            fill=self.theme["bg"], outline=""
        )
        
        # Draw text
        canvas.create_text(
            center, center,
            text="APK",
            fill=self.theme["fg"],
            font=(self.theme["font"], int(size/4), "bold")
        )
    
    def create_footer(self):
        footer_frame = tk.Frame(self.main_container, bg=self.theme["secondary"], height=30)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        # Status label
        self.status_label = tk.Label(
            footer_frame, 
            text="Ready", 
            font=(self.theme["font"], 9),
            bg=self.theme["secondary"],
            fg=self.theme["fg"],
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Version info
        version_label = tk.Label(
            footer_frame, 
            text="v2.0", 
            font=(self.theme["font"], 9),
            bg=self.theme["secondary"],
            fg=self.theme["fg"],
            anchor=tk.E
        )
        version_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def create_signing_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Sign APK")
        
        # Main frame
        main_frame = ttk.Frame(tab, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(title_frame, text="APK Signing Tool", font=(self.theme["font"], 16, "bold"))
        title.pack(side=tk.LEFT, padx=(0, 10))
        
        # Create icon
        icon = IconGenerator.create_icon(24, self.theme["accent"], "sign")
        icon_label = tk.Label(title_frame, image=icon, bg=self.theme["bg"])
        icon_label.image = icon  # Keep a reference
        icon_label.pack(side=tk.LEFT)
        
        # File selection
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="Select APK file:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.apk_entry = ttk.Entry(file_frame, width=50)
        self.apk_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_icon = IconGenerator.create_icon(16, self.theme["fg"], "folder")
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file, image=browse_icon, compound=tk.LEFT)
        browse_btn.image = browse_icon  # Keep a reference
        browse_btn.pack(side=tk.LEFT)
        
        # Drop zone for drag and drop
        self.drop_zone_frame = ttk.LabelFrame(main_frame, text="Or drag APK file here", padding=10)
        self.drop_zone_frame.pack(fill=tk.X, pady=10)
        
        self.drop_zone_label = ttk.Label(
            self.drop_zone_frame, 
            text="📁 Drag and drop APK file here", 
            font=(self.theme["font"], 12),
            foreground="gray"
        )
        self.drop_zone_label.pack(pady=10)
        
        # Progress bar
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill=tk.X, pady=20)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            orient="horizontal", 
            length=100, 
            mode="determinate",
            style="Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill=tk.X)
        
        self.step_label = ttk.Label(self.progress_frame, text="Ready", font=(self.theme["font"], 10))
        self.step_label.pack(pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        sign_icon = IconGenerator.create_icon(16, self.theme["fg"], "sign")
        ttk.Button(
            button_frame, 
            text="Sign APK", 
            command=self.start_sign,
            style="Accent.TButton",
            image=sign_icon,
            compound=tk.LEFT
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        verify_icon = IconGenerator.create_icon(16, self.theme["fg"], "verify")
        ttk.Button(
            button_frame, 
            text="Verify Tools", 
            command=self.verify_tools,
            image=verify_icon,
            compound=tk.LEFT
        ).pack(side=tk.LEFT)
        
        # Output area
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            wrap=tk.WORD, 
            height=10,
            bg=self.theme["secondary"],
            fg=self.theme["fg"],
            font=(self.theme["font"], self.theme["font_size"]),
            relief="flat",
            borderwidth=0
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
    
    def create_batch_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Batch Sign")
        
        main_frame = ttk.Frame(tab, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(title_frame, text="Batch APK Signing", font=(self.theme["font"], 16, "bold"))
        title.pack(side=tk.LEFT, padx=(0, 10))
        
        # Create icon
        icon = IconGenerator.create_icon(24, self.theme["accent"], "batch")
        icon_label = tk.Label(title_frame, image=icon, bg=self.theme["bg"])
        icon_label.image = icon  # Keep a reference
        icon_label.pack(side=tk.LEFT)
        
        # File list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(list_frame, text="APK Files:").pack(anchor=tk.W)
        
        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.batch_listbox = tk.Listbox(
            list_frame, 
            selectmode=tk.MULTIPLE,
            bg=self.theme["secondary"],
            fg=self.theme["fg"],
            selectbackground=self.theme["accent"],
            yscrollcommand=scrollbar.set,
            relief="flat",
            borderwidth=0,
            font=(self.theme["font"], self.theme["font_size"])
        )
        self.batch_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.batch_listbox.yview)
        
        # Drop zone for batch
        self.batch_drop_zone_frame = ttk.LabelFrame(main_frame, text="Or drag APK files here", padding=10)
        self.batch_drop_zone_frame.pack(fill=tk.X, pady=10)
        
        self.batch_drop_zone_label = ttk.Label(
            self.batch_drop_zone_frame, 
            text="📁 Drag and drop APK files here", 
            font=(self.theme["font"], 12),
            foreground="gray"
        )
        self.batch_drop_zone_label.pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        add_icon = IconGenerator.create_icon(16, self.theme["fg"], "folder")
        ttk.Button(button_frame, text="Add APKs", command=self.add_apks, image=add_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 10))
        
        remove_icon = IconGenerator.create_icon(16, self.theme["fg"], "clear")
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected, image=remove_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 10))
        
        clear_icon = IconGenerator.create_icon(16, self.theme["fg"], "clear")
        ttk.Button(button_frame, text="Clear All", command=self.clear_batch, image=clear_icon, compound=tk.LEFT).pack(side=tk.LEFT)
        
        # Progress
        self.batch_progress_frame = ttk.Frame(main_frame)
        self.batch_progress_frame.pack(fill=tk.X, pady=20)
        
        self.batch_progress_bar = ttk.Progressbar(
            self.batch_progress_frame, 
            orient="horizontal", 
            length=100, 
            mode="determinate",
            style="Horizontal.TProgressbar"
        )
        self.batch_progress_bar.pack(fill=tk.X)
        
        self.batch_step_label = ttk.Label(self.batch_progress_frame, text="Ready", font=(self.theme["font"], 10))
        self.batch_step_label.pack(pady=(5, 0))
        
        # Action button
        batch_icon = IconGenerator.create_icon(16, self.theme["fg"], "batch")
        ttk.Button(
            main_frame, 
            text="Start Batch Signing", 
            command=self.start_batch_sign,
            style="Accent.TButton",
            image=batch_icon,
            compound=tk.LEFT
        ).pack(pady=10)
    
    def create_verify_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Verify APK")
        
        # Main frame
        main_frame = ttk.Frame(tab, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(title_frame, text="APK Verification Tool", font=(self.theme["font"], 16, "bold"))
        title.pack(side=tk.LEFT, padx=(0, 10))
        
        # Create icon
        icon = IconGenerator.create_icon(24, self.theme["accent"], "verify")
        icon_label = tk.Label(title_frame, image=icon, bg=self.theme["bg"])
        icon_label.image = icon  # Keep a reference
        icon_label.pack(side=tk.LEFT)
        
        # File selection
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="Select APK file:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.verify_entry = ttk.Entry(file_frame, width=50)
        self.verify_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_icon = IconGenerator.create_icon(16, self.theme["fg"], "folder")
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_verify_file, image=browse_icon, compound=tk.LEFT)
        browse_btn.image = browse_icon  # Keep a reference
        browse_btn.pack(side=tk.LEFT)
        
        # Drop zone for drag and drop
        self.verify_drop_zone_frame = ttk.LabelFrame(main_frame, text="Or drag APK file here", padding=10)
        self.verify_drop_zone_frame.pack(fill=tk.X, pady=10)
        
        self.verify_drop_zone_label = ttk.Label(
            self.verify_drop_zone_frame, 
            text="📁 Drag and drop APK file here", 
            font=(self.theme["font"], 12),
            foreground="gray"
        )
        self.verify_drop_zone_label.pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        verify_icon = IconGenerator.create_icon(16, self.theme["fg"], "verify")
        ttk.Button(
            button_frame, 
            text="Verify APK", 
            command=self.start_verify,
            style="Accent.TButton",
            image=verify_icon,
            compound=tk.LEFT
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Output area
        output_frame = ttk.LabelFrame(main_frame, text="Verification Result", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.verify_text = scrolledtext.ScrolledText(
            output_frame, 
            wrap=tk.WORD, 
            height=10,
            bg=self.theme["secondary"],
            fg=self.theme["fg"],
            font=(self.theme["font"], self.theme["font_size"]),
            relief="flat",
            borderwidth=0
        )
        self.verify_text.pack(fill=tk.BOTH, expand=True)
    
    def create_history_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="History")
        
        main_frame = ttk.Frame(tab, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(title_frame, text="Signing History", font=(self.theme["font"], 16, "bold"))
        title.pack(side=tk.LEFT, padx=(0, 10))
        
        # Create icon
        icon = IconGenerator.create_icon(24, self.theme["accent"], "history")
        icon_label = tk.Label(title_frame, image=icon, bg=self.theme["bg"])
        icon_label.image = icon  # Keep a reference
        icon_label.pack(side=tk.LEFT)
        
        # History list
        history_frame = ttk.Frame(main_frame)
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        columns = ("timestamp", "original_apk", "signed_apk", "status")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        
        # Define headings
        self.history_tree.heading("timestamp", text="Timestamp")
        self.history_tree.heading("original_apk", text="Original APK")
        self.history_tree.heading("signed_apk", text="Signed APK")
        self.history_tree.heading("status", text="Status")
        
        # Configure columns
        self.history_tree.column("timestamp", width=150)
        self.history_tree.column("original_apk", width=300)
        self.history_tree.column("signed_apk", width=300)
        self.history_tree.column("status", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.history_tree.bind("<Double-1>", self.on_history_double_click)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        refresh_icon = IconGenerator.create_icon(16, self.theme["fg"], "refresh")
        ttk.Button(button_frame, text="Refresh", command=self.refresh_history, image=refresh_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 10))
        
        clear_icon = IconGenerator.create_icon(16, self.theme["fg"], "clear")
        ttk.Button(button_frame, text="Clear History", command=self.clear_history, image=clear_icon, compound=tk.LEFT).pack(side=tk.LEFT)
        
        open_icon = IconGenerator.create_icon(16, self.theme["fg"], "open")
        ttk.Button(button_frame, text="Open Output", command=self.open_output_dir, image=open_icon, compound=tk.LEFT).pack(side=tk.LEFT)
        
        # Load initial history
        self.refresh_history()
    
    def create_settings_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Settings")
        
        main_frame = ttk.Frame(tab, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(title_frame, text="Configuration", font=(self.theme["font"], 16, "bold"))
        title.pack(side=tk.LEFT, padx=(0, 10))
        
        # Create icon
        icon = IconGenerator.create_icon(24, self.theme["accent"], "settings")
        icon_label = tk.Label(title_frame, image=icon, bg=self.theme["bg"])
        icon_label.image = icon  # Keep a reference
        icon_label.pack(side=tk.LEFT)
        
        # Settings form
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # JDK Path
        self.create_setting_row(
            settings_frame, 
            "JDK Path:", 
            "JDK_PATH", 
            self.config_manager.get("JDK_PATH"),
            "Select JDK directory"
        )
        
        # SDK Build Tools
        self.create_setting_row(
            settings_frame, 
            "SDK Build Tools:", 
            "SDK_BUILD_TOOLS", 
            self.config_manager.get("SDK_BUILD_TOOLS"),
            "Select SDK build-tools directory"
        )
        
        # Keystore
        self.create_setting_row(
            settings_frame, 
            "Keystore File:", 
            "KEYSTORE", 
            self.config_manager.get("KEYSTORE"),
            "Select keystore file",
            file_types=[("JKS files", "*.jks"), ("All files", "*.*")]
        )
        
        # Store Password
        self.create_setting_row(
            settings_frame, 
            "Store Password:", 
            "STOREPASS", 
            self.config_manager.get("STOREPASS"),
            password=True
        )
        
        # Key Password
        self.create_setting_row(
            settings_frame, 
            "Key Password:", 
            "KEYPASS", 
            self.config_manager.get("KEYPASS"),
            password=True
        )
        
        # Alias
        self.create_setting_row(
            settings_frame, 
            "Key Alias:", 
            "ALIAS", 
            self.config_manager.get("ALIAS")
        )
        
        # Output Directory
        self.create_setting_row(
            settings_frame, 
            "Output Directory:", 
            "OUTPUT_DIR", 
            self.config_manager.get("OUTPUT_DIR"),
            "Select output directory"
        )
        
        # Log Level
        log_frame = ttk.Frame(settings_frame)
        log_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(log_frame, text="Log Level:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.log_level_var = tk.StringVar(value=self.config_manager.get("LOG_LEVEL"))
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        log_level_combo = ttk.Combobox(
            log_frame, 
            textvariable=self.log_level_var, 
            values=log_levels,
            state="readonly"
        )
        log_level_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, pady=10)
        
        self.auto_open_var = tk.BooleanVar(value=self.config_manager.get("AUTO_OPEN_OUTPUT", True))
        ttk.Checkbutton(
            options_frame, 
            text="Open output directory after signing", 
            variable=self.auto_open_var
        ).pack(anchor=tk.W, pady=5)
        
        self.copy_clipboard_var = tk.BooleanVar(value=self.config_manager.get("COPY_TO_CLIPBOARD", True))
        ttk.Checkbutton(
            options_frame, 
            text="Copy signed APK path to clipboard", 
            variable=self.copy_clipboard_var
        ).pack(anchor=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        save_icon = IconGenerator.create_icon(16, self.theme["fg"], "save")
        ttk.Button(
            button_frame, 
            text="Save Settings", 
            command=self.save_settings,
            style="Accent.TButton",
            image=save_icon,
            compound=tk.LEFT
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        reset_icon = IconGenerator.create_icon(16, self.theme["fg"], "clear")
        ttk.Button(
            button_frame, 
            text="Reset to Defaults", 
            command=self.reset_settings,
            image=reset_icon,
            compound=tk.LEFT
        ).pack(side=tk.LEFT)
    
    def create_log_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Logs")
        
        main_frame = ttk.Frame(tab, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(title_frame, text="Application Logs", font=(self.theme["font"], 16, "bold"))
        title.pack(side=tk.LEFT, padx=(0, 10))
        
        # Create icon
        icon = IconGenerator.create_icon(24, self.theme["accent"], "log")
        icon_label = tk.Label(title_frame, image=icon, bg=self.theme["bg"])
        icon_label.image = icon  # Keep a reference
        icon_label.pack(side=tk.LEFT)
        
        # Log display
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD,
            bg=self.theme["secondary"],
            fg=self.theme["fg"],
            font=(self.theme["font"], self.theme["font_size"]),
            relief="flat",
            borderwidth=0
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        refresh_icon = IconGenerator.create_icon(16, self.theme["fg"], "refresh")
        ttk.Button(button_frame, text="Refresh", command=self.refresh_logs, image=refresh_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 10))
        
        clear_icon = IconGenerator.create_icon(16, self.theme["fg"], "clear")
        ttk.Button(button_frame, text="Clear Logs", command=self.clear_logs, image=clear_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 10))
        
        export_icon = IconGenerator.create_icon(16, self.theme["fg"], "export")
        ttk.Button(button_frame, text="Export Logs", command=self.export_logs, image=export_icon, compound=tk.LEFT).pack(side=tk.LEFT)
        
        # Initial load
        self.refresh_logs()
    
    def create_about_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="About")
        
        main_frame = ttk.Frame(tab, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(title_frame, text="About APK Super Signer Pro", font=(self.theme["font"], 16, "bold"))
        title.pack(side=tk.LEFT, padx=(0, 10))
        
        # Create icon
        icon = IconGenerator.create_icon(24, self.theme["accent"], "info")
        icon_label = tk.Label(title_frame, image=icon, bg=self.theme["bg"])
        icon_label.image = icon  # Keep a reference
        icon_label.pack(side=tk.LEFT)
        
        # Content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo
        logo_frame = ttk.Frame(content_frame)
        logo_frame.pack(pady=20)
        
        logo_canvas = tk.Canvas(logo_frame, width=100, height=100, bg=self.theme["bg"], highlightthickness=0)
        logo_canvas.pack()
        self.draw_apk_icon(logo_canvas, 100, self.theme["accent"])
        
        # App info
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(pady=10)
        
        app_name = ttk.Label(info_frame, text="APK Super Signer Pro", font=(self.theme["font"], 18, "bold"))
        app_name.pack(pady=5)
        
        version = ttk.Label(info_frame, text="Version 2.0", font=(self.theme["font"], 12))
        version.pack(pady=5)
        
        description = ttk.Label(
            info_frame, 
            text="A professional tool for signing Android APK files with multiple themes and advanced features.",
            font=(self.theme["font"], 10),
            wraplength=500
        )
        description.pack(pady=10)
        
        # Features
        features_frame = ttk.LabelFrame(content_frame, text="Features", padding=10)
        features_frame.pack(fill=tk.X, pady=10)
        
        features = [
            "• Sign APK files with custom keystore",
            "• Batch signing for multiple APKs",
            "• Verify APK signatures",
            "• Multiple theme options",
            "• Detailed signing history",
            "• Automatic tool detection",
            "• Export logs and history"
        ]
        
        for feature in features:
            ttk.Label(features_frame, text=feature, font=(self.theme["font"], 10)).pack(anchor=tk.W, pady=2)
        
        # System info
        sys_frame = ttk.LabelFrame(content_frame, text="System Information", padding=10)
        sys_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(sys_frame, text=f"OS: {platform.system()} {platform.release()}", font=(self.theme["font"], 10)).pack(anchor=tk.W, pady=2)
        ttk.Label(sys_frame, text=f"Python: {platform.python_version()}", font=(self.theme["font"], 10)).pack(anchor=tk.W, pady=2)
        ttk.Label(sys_frame, text=f"Tcl/Tk: {tk.TkVersion}", font=(self.theme["font"], 10)).pack(anchor=tk.W, pady=2)
        
        # Links
        links_frame = ttk.Frame(content_frame)
        links_frame.pack(pady=20)
        
        github_btn = ttk.Button(
            links_frame, 
            text="GitHub Repository", 
            command=lambda: webbrowser.open("https://github.com/TssHack/apk-signer/")
        )
        github_btn.pack(side=tk.LEFT, padx=5)
        
        help_btn = ttk.Button(
            links_frame, 
            text="Documentation", 
            command=lambda: webbrowser.open("https://docs.ehsanjs.ir/apk-signer")
        )
        help_btn.pack(side=tk.LEFT, padx=5)
        
        # Copyright
        copyright_label = ttk.Label(
            content_frame, 
            text="© 2023 APK Super Signer Pro. All rights reserved.",
            font=(self.theme["font"], 9)
        )
        copyright_label.pack(pady=20)
    
    def create_setting_row(self, parent, label_text, config_key, default_value, browse_title=None, password=False, file_types=None):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text=label_text).pack(side=tk.LEFT, padx=(0, 10))
        
        entry = ttk.Entry(frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry.insert(0, default_value)
        
        if password:
            entry.config(show="*")
        
        if browse_title:
            def browse():
                if file_types:
                    path = filedialog.askopenfilename(title=browse_title, filetypes=file_types)
                else:
                    path = filedialog.askdirectory(title=browse_title)
                
                if path:
                    entry.delete(0, tk.END)
                    entry.insert(0, path)
            
            browse_icon = IconGenerator.create_icon(16, self.theme["fg"], "folder")
            browse_btn = ttk.Button(frame, text="Browse", command=browse, image=browse_icon, compound=tk.LEFT)
            browse_btn.image = browse_icon  # Keep a reference
            browse_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Store reference
        setattr(self, f"{config_key}_entry", entry)
    
    def setup_drag_drop_fallback(self):
        """Setup basic drag and drop using tkinter's built-in capabilities"""
        # Make the drop zones accept drops
        self.drop_zone_frame.bind("<Enter>", lambda e: self.on_drop_zone_enter(self.drop_zone_label))
        self.drop_zone_frame.bind("<Leave>", lambda e: self.on_drop_zone_leave(self.drop_zone_label))
        self.drop_zone_frame.bind("<Button-1>", lambda e: self.browse_file())
        
        self.batch_drop_zone_frame.bind("<Enter>", lambda e: self.on_drop_zone_enter(self.batch_drop_zone_label))
        self.batch_drop_zone_frame.bind("<Leave>", lambda e: self.on_drop_zone_leave(self.batch_drop_zone_label))
        self.batch_drop_zone_frame.bind("<Button-1>", lambda e: self.add_apks())
        
        self.verify_drop_zone_frame.bind("<Enter>", lambda e: self.on_drop_zone_enter(self.verify_drop_zone_label))
        self.verify_drop_zone_frame.bind("<Leave>", lambda e: self.on_drop_zone_leave(self.verify_drop_zone_label))
        self.verify_drop_zone_frame.bind("<Button-1>", lambda e: self.browse_verify_file())
        
        # Bind paste events for file paths
        self.apk_entry.bind("<Control-v>", lambda e: self.paste_file_path(e, self.apk_entry))
        self.verify_entry.bind("<Control-v>", lambda e: self.paste_file_path(e, self.verify_entry))
        self.root.bind("<<Paste>>", lambda e: self.handle_paste())
    
    def on_drop_zone_enter(self, label):
        label.config(foreground=self.theme["accent"])
    
    def on_drop_zone_leave(self, label):
        label.config(foreground="gray")
    
    def paste_file_path(self, event, widget):
        try:
            clipboard_content = self.root.clipboard_get()
            if clipboard_content.endswith('.apk'):
                widget.delete(0, tk.END)
                widget.insert(0, clipboard_content.strip())
                return "break"
        except:
            pass
        return None
    
    def handle_paste(self):
        # Handle global paste events
        focused_widget = self.root.focus_get()
        if focused_widget == self.apk_entry:
            self.paste_file_path(None, self.apk_entry)
        elif focused_widget == self.verify_entry:
            self.paste_file_path(None, self.verify_entry)
    
    def set_window_icon(self):
        try:
            # Create a custom icon
            icon_img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon_img)
            
            # Draw a stylized APK icon
            padding = 10
            draw.rectangle([padding, padding, 64-padding, 64-padding], fill=self.theme["accent"])
            draw.polygon([32, padding+5, 64-padding-5, 64-padding-5, padding+5, 64-padding-5], fill=self.theme["bg"])
            draw.text((32, 32), "APK", fill=self.theme["fg"], anchor="mm", font=ImageFont.truetype("arial.ttf", 16))
            
            icon = ImageTk.PhotoImage(icon_img)
            self.root.iconphoto(True, icon)
        except Exception as e:
            logging.error(f"Error setting window icon: {e}")
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def change_theme(self, event=None):
        selected_theme = self.theme_var.get()
        if selected_theme != self.current_theme:
            self.set_theme(selected_theme)
            self.config_manager.set("THEME", selected_theme)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select APK file",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        if file_path:
            self.apk_entry.delete(0, tk.END)
            self.apk_entry.insert(0, file_path)
    
    def browse_verify_file(self):
        file_path = filedialog.askopenfilename(
            title="Select APK file",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        if file_path:
            self.verify_entry.delete(0, tk.END)
            self.verify_entry.insert(0, file_path)
    
    def start_sign(self):
        apk_path = self.apk_entry.get()
        if not apk_path or not os.path.isfile(apk_path):
            messagebox.showerror("Error", "Please select a valid APK file.")
            return
        
        # Check if keystore is configured
        if not self.config_manager.get("KEYSTORE"):
            messagebox.showerror("Error", "Keystore not configured. Please set up keystore in Settings.")
            return
        
        # Reset progress
        self.progress_bar['value'] = 0
        self.step_label.config(text="Starting signing process...")
        self.status_label.config(text="Signing APK...")
        self.output_text.delete(1.0, tk.END)
        
        # Start signing in a separate thread
        threading.Thread(
            target=self.signer.sign_apk,
            args=(apk_path, self.progress_queue),
            daemon=True
        ).start()
    
    def verify_tools(self):
        try:
            self.signer.verify_tools()
            messagebox.showinfo("Success", "All required tools are properly configured!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def start_verify(self):
        apk_path = self.verify_entry.get()
        if not apk_path or not os.path.isfile(apk_path):
            messagebox.showerror("Error", "Please select a valid APK file.")
            return
        
        # Reset progress
        self.verify_text.delete(1.0, tk.END)
        self.status_label.config(text="Verifying APK...")
        
        # Start verification in a separate thread
        threading.Thread(
            target=self.signer.verify_apk,
            args=(apk_path, self.progress_queue),
            daemon=True
        ).start()
    
    def add_apks(self):
        file_paths = filedialog.askopenfilenames(
            title="Select APK files",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        for path in file_paths:
            if path not in self.batch_listbox.get(0, tk.END):
                self.batch_listbox.insert(tk.END, path)
    
    def remove_selected(self):
        selected = self.batch_listbox.curselection()
        for index in reversed(selected):
            self.batch_listbox.delete(index)
    
    def clear_batch(self):
        self.batch_listbox.delete(0, tk.END)
    
    def start_batch_sign(self):
        apk_paths = self.batch_listbox.get(0, tk.END)
        if not apk_paths:
            messagebox.showerror("Error", "No APK files selected for batch signing.")
            return
        
        # Check if keystore is configured
        if not self.config_manager.get("KEYSTORE"):
            messagebox.showerror("Error", "Keystore not configured. Please set up keystore in Settings.")
            return
        
        # Reset progress
        self.batch_progress_bar['value'] = 0
        self.batch_step_label.config(text="Starting batch signing...")
        self.status_label.config(text="Batch signing APKs...")
        
        # Start batch signing in a separate thread
        threading.Thread(
            target=self.signer.batch_sign,
            args=(apk_paths, self.progress_queue),
            daemon=True
        ).start()
    
    def refresh_history(self):
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add history items
        for entry in self.signer.history:
            self.history_tree.insert(
                "", 
                tk.END, 
                values=(
                    entry["timestamp"],
                    entry["original_apk"],
                    entry["signed_apk"],
                    entry["status"]
                )
            )
    
    def clear_history(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the history?"):
            self.signer.history = []
            self.signer.save_history()
            self.refresh_history()
    
    def on_history_double_click(self, event):
        # Get selected item
        selected_item = self.history_tree.selection()
        if not selected_item:
            return
        
        # Get values
        values = self.history_tree.item(selected_item[0], "values")
        signed_apk_path = values[2]
        
        # Show details dialog
        self.show_history_details(values)
    
    def show_history_details(self, values):
        # Create details dialog
        details_window = tk.Toplevel(self.root)
        details_window.title("Signing Details")
        details_window.geometry("600x400")
        details_window.resizable(False, False)
        
        # Apply theme
        details_window.config(bg=self.theme["bg"])
        
        # Main frame
        main_frame = tk.Frame(details_window, bg=self.theme["bg"], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(
            main_frame, 
            text="Signing Details", 
            font=(self.theme["font"], 16, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["fg"]
        )
        title.pack(pady=(0, 20))
        
        # Details
        details_frame = tk.Frame(main_frame, bg=self.theme["bg"])
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Timestamp
        tk.Label(
            details_frame, 
            text="Timestamp:", 
            font=(self.theme["font"], 10, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["fg"]
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        tk.Label(
            details_frame, 
            text=values[0], 
            font=(self.theme["font"], 10),
            bg=self.theme["bg"],
            fg=self.theme["fg"]
        ).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Original APK
        tk.Label(
            details_frame, 
            text="Original APK:", 
            font=(self.theme["font"], 10, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["fg"]
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        tk.Label(
            details_frame, 
            text=values[1], 
            font=(self.theme["font"], 10),
            bg=self.theme["bg"],
            fg=self.theme["fg"],
            wraplength=400
        ).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Signed APK
        tk.Label(
            details_frame, 
            text="Signed APK:", 
            font=(self.theme["font"], 10, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["fg"]
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        tk.Label(
            details_frame, 
            text=values[2], 
            font=(self.theme["font"], 10),
            bg=self.theme["bg"],
            fg=self.theme["fg"],
            wraplength=400
        ).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Status
        tk.Label(
            details_frame, 
            text="Status:", 
            font=(self.theme["font"], 10, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["fg"]
        ).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        status_color = self.theme["success"] if values[3] == "success" else self.theme["error"]
        tk.Label(
            details_frame, 
            text=values[3].capitalize(), 
            font=(self.theme["font"], 10, "bold"),
            bg=self.theme["bg"],
            fg=status_color
        ).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Find hash information
        original_hash = ""
        signed_hash = ""
        
        for entry in self.signer.history:
            if entry["timestamp"] == values[0] and entry["signed_apk"] == values[2]:
                original_hash = entry.get("original_hash", "")
                signed_hash = entry.get("signed_hash", "")
                break
        
        if original_hash:
            tk.Label(
                details_frame, 
                text="Original Hash:", 
                font=(self.theme["font"], 10, "bold"),
                bg=self.theme["bg"],
                fg=self.theme["fg"]
            ).grid(row=4, column=0, sticky=tk.W, pady=5)
            
            tk.Label(
                details_frame, 
                text=original_hash, 
                font=(self.theme["font"], 9),
                bg=self.theme["bg"],
                fg=self.theme["fg"],
                wraplength=400
            ).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        if signed_hash:
            tk.Label(
                details_frame, 
                text="Signed Hash:", 
                font=(self.theme["font"], 10, "bold"),
                bg=self.theme["bg"],
                fg=self.theme["fg"]
            ).grid(row=5, column=0, sticky=tk.W, pady=5)
            
            tk.Label(
                details_frame, 
                text=signed_hash, 
                font=(self.theme["font"], 9),
                bg=self.theme["bg"],
                fg=self.theme["fg"],
                wraplength=400
            ).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.theme["bg"])
        button_frame.pack(fill=tk.X, pady=20)
        
        # Open button
        open_icon = IconGenerator.create_icon(16, self.theme["fg"], "open")
        open_btn = tk.Button(
            button_frame, 
            text="Open Signed APK", 
            command=lambda: self.open_file(values[2]),
            bg=self.theme["accent"],
            fg=self.theme["fg"],
            font=(self.theme["font"], 10, "bold"),
            image=open_icon,
            compound=tk.LEFT
        )
        open_btn.image = open_icon  # Keep a reference
        open_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Copy button
        copy_icon = IconGenerator.create_icon(16, self.theme["fg"], "copy")
        copy_btn = tk.Button(
            button_frame, 
            text="Copy Path", 
            command=lambda: self.copy_to_clipboard(values[2]),
            bg=self.theme["accent"],
            fg=self.theme["fg"],
            font=(self.theme["font"], 10, "bold"),
            image=copy_icon,
            compound=tk.LEFT
        )
        copy_btn.image = copy_icon  # Keep a reference
        copy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_btn = tk.Button(
            button_frame, 
            text="Close", 
            command=details_window.destroy,
            bg=self.theme["tertiary"],
            fg=self.theme["fg"],
            font=(self.theme["font"], 10, "bold")
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Center the window
        details_window.update_idletasks()
        width = details_window.winfo_width()
        height = details_window.winfo_height()
        x = (details_window.winfo_screenwidth() // 2) - (width // 2)
        y = (details_window.winfo_screenheight() // 2) - (height // 2)
        details_window.geometry(f'{width}x{height}+{x}+{y}')
    
    def open_file(self, file_path):
        try:
            if os.path.exists(file_path):
                if platform.system() == "Windows":
                    os.startfile(file_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", file_path])
                else:  # Linux
                    subprocess.run(["xdg-open", file_path])
            else:
                messagebox.showerror("Error", "File not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Success", "Path copied to clipboard!")
    
    def open_output_dir(self):
        output_dir = self.config_manager.get("OUTPUT_DIR")
        if os.path.exists(output_dir):
            self.open_file(output_dir)
        else:
            messagebox.showerror("Error", "Output directory not found.")
    
    def save_settings(self):
        # Save all settings
        self.config_manager.set("JDK_PATH", self.JDK_PATH_entry.get())
        self.config_manager.set("SDK_BUILD_TOOLS", self.SDK_BUILD_TOOLS_entry.get())
        self.config_manager.set("KEYSTORE", self.KEYSTORE_entry.get())
        self.config_manager.set("STOREPASS", self.STOREPASS_entry.get())
        self.config_manager.set("KEYPASS", self.KEYPASS_entry.get())
        self.config_manager.set("ALIAS", self.ALIAS_entry.get())
        self.config_manager.set("OUTPUT_DIR", self.OUTPUT_DIR_entry.get())
        self.config_manager.set("LOG_LEVEL", self.log_level_var.get())
        self.config_manager.set("AUTO_OPEN_OUTPUT", self.auto_open_var.get())
        self.config_manager.set("COPY_TO_CLIPBOARD", self.copy_clipboard_var.get())
        
        messagebox.showinfo("Success", "Settings saved successfully!")
    
    def reset_settings(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to reset all settings to defaults?"):
            # Reset config manager
            self.config_manager.config = self.config_manager.load_config()
            self.config_manager.save_config()
            
            # Reload settings in UI
            self.JDK_PATH_entry.delete(0, tk.END)
            self.JDK_PATH_entry.insert(0, self.config_manager.get("JDK_PATH"))
            self.SDK_BUILD_TOOLS_entry.delete(0, tk.END)
            self.SDK_BUILD_TOOLS_entry.insert(0, self.config_manager.get("SDK_BUILD_TOOLS"))
            self.KEYSTORE_entry.delete(0, tk.END)
            self.KEYSTORE_entry.insert(0, self.config_manager.get("KEYSTORE"))
            self.STOREPASS_entry.delete(0, tk.END)
            self.STOREPASS_entry.insert(0, self.config_manager.get("STOREPASS"))
            self.KEYPASS_entry.delete(0, tk.END)
            self.KEYPASS_entry.insert(0, self.config_manager.get("KEYPASS"))
            self.ALIAS_entry.delete(0, tk.END)
            self.ALIAS_entry.insert(0, self.config_manager.get("ALIAS"))
            self.OUTPUT_DIR_entry.delete(0, tk.END)
            self.OUTPUT_DIR_entry.insert(0, self.config_manager.get("OUTPUT_DIR"))
            self.log_level_var.set(self.config_manager.get("LOG_LEVEL"))
            self.auto_open_var.set(self.config_manager.get("AUTO_OPEN_OUTPUT", True))
            self.copy_clipboard_var.set(self.config_manager.get("COPY_TO_CLIPBOARD", True))
            
            messagebox.showinfo("Success", "Settings reset to defaults!")
    
    def refresh_logs(self):
        self.log_text.delete(1.0, tk.END)
        try:
            log_dir = Path("logs")
            if log_dir.exists():
                log_files = sorted(log_dir.glob("*.log"), reverse=True)
                if log_files:
                    with open(log_files[0], 'r') as f:
                        self.log_text.insert(tk.END, f.read())
        except Exception as e:
            self.log_text.insert(tk.END, f"Error loading logs: {str(e)}")
    
    def clear_logs(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all logs?"):
            self.log_text.delete(1.0, tk.END)
            try:
                log_dir = Path("logs")
                if log_dir.exists():
                    shutil.rmtree(log_dir)
                    log_dir.mkdir()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear logs: {str(e)}")
    
    def export_logs(self):
        file_path = filedialog.asksaveasfilename(
            title="Export Logs",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", "Logs exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export logs: {str(e)}")
    
    def on_window_resize(self, event):
        # Save window geometry
        if event.widget == self.root:
            self.config_manager.set("WINDOW_GEOMETRY", f"{event.width}x{event.height}")
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.root.destroy()
    
    def process_progress_queue(self):
        try:
            while True:
                msg_type, *data = self.progress_queue.get_nowait()
                
                if msg_type == "progress":
                    value, text = data
                    self.progress_bar['value'] = value * 100
                    self.step_label.config(text=text)
                    self.status_label.config(text=f"Signing: {text}")
                
                elif msg_type == "log":
                    text = data[0]
                    self.output_text.insert(tk.END, f"{text}\n")
                    self.output_text.see(tk.END)
                
                elif msg_type == "error":
                    text = data[0]
                    self.output_text.insert(tk.END, f"ERROR: {text}\n", "error")
                    self.output_text.see(tk.END)
                    self.output_text.tag_config("error", foreground=self.theme["error"])
                
                elif msg_type == "complete":
                    output_path = data[0]
                    self.step_label.config(text="Signing completed successfully!")
                    self.status_label.config(text="Ready")
                    
                    # Auto open output directory
                    if self.config_manager.get("AUTO_OPEN_OUTPUT", True):
                        self.open_file(os.path.dirname(output_path))
                    
                    # Copy to clipboard
                    if self.config_manager.get("COPY_TO_CLIPBOARD", True):
                        self.copy_to_clipboard(output_path)
                    
                    messagebox.showinfo("Success", f"Signed APK saved to:\n{output_path}")
                
                elif msg_type == "failed":
                    error = data[0]
                    self.step_label.config(text="Signing failed!")
                    self.status_label.config(text="Ready")
                    messagebox.showerror("Error", f"Signing failed:\n{error}")
                
                elif msg_type == "batch_progress":
                    value, text = data
                    self.batch_progress_bar['value'] = value * 100
                    self.batch_step_label.config(text=text)
                    self.status_label.config(text=f"Batch: {text}")
                
                elif msg_type == "batch_complete":
                    results = data[0]
                    self.batch_step_label.config(text="Batch signing completed!")
                    self.status_label.config(text="Ready")
                    
                    # Show results
                    success_count = sum(1 for r in results if r["status"] == "success")
                    total_count = len(results)
                    
                    messagebox.showinfo(
                        "Batch Results",
                        f"Batch signing completed:\n"
                        f"Success: {success_count}/{total_count}\n"
                        f"Failed: {total_count - success_count}/{total_count}"
                    )
                    
                    # Auto open output directory
                    if success_count > 0 and self.config_manager.get("AUTO_OPEN_OUTPUT", True):
                        self.open_output_dir()
                    
                    # Clear batch list
                    self.batch_listbox.delete(0, tk.END)
                
                elif msg_type == "verify_complete":
                    output = data[0]
                    self.verify_text.insert(tk.END, f"Verification successful!\n\n{output}\n")
                    self.verify_text.see(tk.END)
                    self.status_label.config(text="Ready")
                    messagebox.showinfo("Success", "APK verification successful!")
                
                elif msg_type == "verify_failed":
                    error = data[0]
                    self.verify_text.insert(tk.END, f"Verification failed: {error}\n", "error")
                    self.verify_text.see(tk.END)
                    self.verify_text.tag_config("error", foreground=self.theme["error"])
                    self.status_label.config(text="Ready")
                    messagebox.showerror("Error", f"APK verification failed:\n{error}")
                
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_progress_queue)

# ------------------- Main Application -------------------
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ApkSignerGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QLibraryInfo
from pywinauto import Desktop, findwindows, keyboard, timings
from pywinauto.application import Application


ROOT = Path(__file__).resolve().parents[2]


def _start_app() -> subprocess.Popen:
    env = dict(**os.environ)
    env["QT_QPA_PLATFORM"] = "windows"
    plugins_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
    if plugins_path:
        env["QT_PLUGIN_PATH"] = plugins_path
        env["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(plugins_path, "platforms")
    return subprocess.Popen(
        [sys.executable, "-m", "app.composition_root.gui_main"],
        cwd=ROOT,
        env=env,
    )


def _connect_app(pid: int, timeout: float = 30.0) -> Application:
    def _connect() -> Application:
        return Application(backend="win32").connect(process=pid)

    return timings.wait_until_passes(timeout, 0.5, _connect)


def _terminate(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)


def _find_window(proc: subprocess.Popen, timeout: float = 90.0):
    def _pick():
        if proc.poll() is not None:
            raise RuntimeError(f"App exited with code {proc.returncode}")
        pid = proc.pid
        handles = findwindows.find_windows(process=pid, visible_only=True)
        if not handles:
            handles = findwindows.find_windows(process=pid)
        if not handles:
            handles = findwindows.find_windows(title_re=".*Manga Translator.*", visible_only=True)
        if not handles:
            handles = findwindows.find_windows(title_re=".*Manga Translator.*")
        if not handles:
            raise RuntimeError("No windows yet")

        desktop = Desktop(backend="win32")
        candidates = [desktop.window(handle=handle) for handle in handles]
        for win in candidates:
            title = win.window_text()
            if "Manga Translator" in title:
                return win
        return candidates[0]

    return timings.wait_until_passes(timeout, 0.5, _pick)


def _list_window_titles(pid: int) -> list[str]:
    handles = findwindows.find_windows(process=pid)
    if not handles:
        handles = findwindows.find_windows()
    desktop = Desktop(backend="win32")
    titles: list[str] = []
    for handle in handles:
        try:
            titles.append(desktop.window(handle=handle).window_text())
        except Exception:
            continue
    return titles


def _find_dialog(proc: subprocess.Popen, title: str, timeout: float = 20.0):
    def _pick():
        if proc.poll() is not None:
            raise RuntimeError(f"App exited with code {proc.returncode}")
        pid = proc.pid
        handles = findwindows.find_windows(title_re=f".*{title}.*", process=pid, visible_only=True)
        if not handles:
            handles = findwindows.find_windows(title_re=f".*{title}.*", process=pid)
        if not handles:
            handles = findwindows.find_windows(title_re=f".*{title}.*", visible_only=True)
        if not handles:
            handles = findwindows.find_windows(title_re=f".*{title}.*")
        if handles:
            return Desktop(backend="win32").window(handle=handles[0])

        uia_desktop = Desktop(backend="uia")
        windows = list(uia_desktop.windows())
        for win in windows:
            name = win.window_text() or win.element_info.name or ""
            if title.lower() in name.lower():
                return win
            try:
                label = win.child_window(title_re=".*Project name.*", control_type="Text")
                if label.exists():
                    return win
            except Exception:
                continue

        titles = _list_window_titles(pid)
        raise RuntimeError(f"{title} dialog not found. Windows: {titles}")

    return timings.wait_until_passes(timeout, 0.5, _pick)


def test_blackbox_main_window_smoke() -> None:
    proc = _start_app()
    app = None
    window = None
    try:
        app = _connect_app(proc.pid)
        window = _find_window(proc)
        window.wait("exists visible", timeout=30)
        assert window.exists()
    finally:
        if window is not None:
            try:
                window.close()
            except Exception:
                pass
        _terminate(proc)


def test_blackbox_new_project_via_menu() -> None:
    proc = _start_app()
    app = None
    window = None
    try:
        app = _connect_app(proc.pid)
        window = _find_window(proc)
        window.wait("exists visible", timeout=30)
        window.set_focus()

        keyboard.send_keys("^n", pause=0.05)
        dialog = _find_dialog(proc, "New Project", timeout=15.0)

        dialog.set_focus()
        text_set = False
        try:
            edit = dialog.child_window(control_type="Edit")
            edit.wait("exists enabled", timeout=5)
            try:
                edit.set_edit_text("Demo")
                text_set = True
            except Exception:
                edit.click_input()
        except Exception:
            pass

        if not text_set:
            try:
                dialog.type_keys("^a{BACKSPACE}Demo", set_foreground=True)
            except Exception:
                keyboard.send_keys("^a{BACKSPACE}Demo", pause=0.05)

        try:
            ok_button = dialog.child_window(title="OK", control_type="Button")
            if ok_button.exists():
                ok_button.click_input()
            else:
                keyboard.send_keys("{ENTER}")
        except Exception:
            keyboard.send_keys("{ENTER}")

        timings.wait_until_passes(
            20,
            0.5,
            lambda: "Demo" in window.window_text(),
        )
        assert "Demo" in window.window_text()
    finally:
        if window is not None:
            try:
                window.close()
            except Exception:
                pass
        _terminate(proc)

from pathlib import Path

from app.scripts import run_pipeline


class FakeRunner:
    def __init__(self):
        self.loaded = None

    def load(self, path: Path) -> None:
        self.loaded = path

    def run(self, inputs: dict) -> dict:
        return {"image": [1, 2, 3]}

    def cleanup(self) -> None:
        pass


def test_run_pipeline_cli_saves_output(monkeypatch, tmp_path, capsys):
    pipeline_path = tmp_path / "pipe.pygraph"
    pipeline_path.write_text("{}")
    image_path = tmp_path / "img.bin"
    image_path.write_bytes(b"\x00\x01")
    output_path = tmp_path / "out.txt"

    monkeypatch.setattr(run_pipeline, "PyFlowGraphRunner", lambda: FakeRunner())

    exit_code = run_pipeline.main(
        [
            "--pipeline",
            str(pipeline_path),
            "--image",
            str(image_path),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.exists()
    captured = capsys.readouterr()
    assert "Pipeline succeeded" in captured.out

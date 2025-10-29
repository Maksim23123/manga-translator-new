# PyFlow (Embedded Copy)

This folder contains a local copy of [PyFlow](https://github.com/wonderworks-software/PyFlow),
a visual scripting framework for Python and Qt.

It was forked and embedded into this project for tighter integration and modification.

## Source

- Original repo: https://github.com/wonderworks-software/PyFlow
- Forked by: @Maksim23123
- Commit: `4edba796e6e40565e46ce718ca52eeb5c84219cd` from `master` branch
- Date: July 7, 2025

## License

PyFlow is licensed under the [Apache License 2.0](../LICENSE).  
This copy retains the original LICENSE and follows the terms of redistribution and modification.

## Purpose in This Project

PyFlow is used as the foundation for the graph editor (pipeline editor) component of the Manga Translator app.  
We have integrated it directly to allow:
- Custom nodes specific to manga processing
- Custom serialization of pipelines
- Tighter UI integration via PySide6
- Long-term stability and independence from upstream changes

## Notes

This version may differ from the upstream version.  
Please refer to this fork for any modifications made.
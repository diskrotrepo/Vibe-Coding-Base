# Vibe-Coding-Base
An experimental base to make future vibe coding simpler

## Linter

This repository includes a Dart-based linter located in `linter/`.
To enforce the rules automatically, configure git to use the
provided pre-commit hook:

```sh
git config core.hooksPath .githooks
```

After setting the hook path, every commit will run `dart linter/linter.dart .`
and abort if any rule violations are found.

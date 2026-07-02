# GitHub Upload Guide

This project is ready to upload as a normal GitHub repository. Runtime files such as `.venv`, `build`, `dist`, `config.json`, and logs are ignored by `.gitignore`.

## Create a GitHub repository

Create an empty repository on GitHub named:

```text
MouseTranslatorPro
```

Do not initialize it with a README, because this project already contains one.

## Push the source code

Replace `YOUR_NAME` with your GitHub account or organization:

```powershell
cd /d D:\MouseTranslatorPro
git remote add origin https://github.com/YOUR_NAME/MouseTranslatorPro.git
git branch -M main
git push -u origin main
```

If GitHub asks for a password, use a GitHub Personal Access Token instead of your account password.

## Upload the packaged EXE as a GitHub Release

The local build output is:

```text
D:\MouseTranslatorPro\dist\MouseTranslatorPro\MouseTranslatorPro.exe
```

The release zip is:

```text
D:\MouseTranslatorPro\release\MouseTranslatorPro-v0.1.0-win64.zip
```

On GitHub, open the repository, go to **Releases**, create tag `v0.1.0`, and upload the zip file above.

## Optional: use GitHub CLI

If you install and log in to GitHub CLI:

```powershell
gh auth login
gh repo create MouseTranslatorPro --public --source=. --remote=origin --push
gh release create v0.1.0 .\release\MouseTranslatorPro-v0.1.0-win64.zip --title "MouseTranslatorPro v0.1.0" --notes-file RELEASE_NOTES.md
```

Use `--private` instead of `--public` if you want a private repository.

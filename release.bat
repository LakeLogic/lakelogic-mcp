@echo off
REM -- LakeLogic MCP Release Script -----------------------------------------
REM Same shape as the OLC and LakeLogic release.bat, so all three repos cut releases the same way.
REM
REM Usage:   release.bat           (auto-detect bump: patch/minor/major)
REM          release.bat minor     (force minor bump)
REM          release.bat major     (force major bump)
REM
REM Prerequisites:
REM   uv                           (commitizen runs through uvx; nothing to install)
REM   winget install git-cliff     (or: cargo install git-cliff)
REM
REM What it does:
REM   0.  pytest              - the server's tests (abort if they fail)
REM   0a. docs build          - mkdocs build --strict, if mkdocs is installed (abort on fail)
REM   1.  cz bump             - bumps the version in all five places + git tag
REM                             (pyproject.toml, __init__.py, server.json x2, plugin.json)
REM   2.  git cliff           - regenerates CHANGELOG.md from all tags (cliff.toml)
REM   3.  git commit amend    - folds the changelog into the bump commit
REM   4.  git tag -f -a       - re-attaches the tag to the amended commit
REM   5.  git push            - pushes everything incl. tags
REM
REM The pushed tag triggers publish.yml (tests + PyPI via Trusted Publishing), which then
REM triggers registry.yml (the official MCP Registry listing). Pushing main also redeploys
REM the docs site (docs.yml).
REM
REM -----------------------------------------------------------------------
REM IMPORTANT: Commit Message Format
REM -----------------------------------------------------------------------
REM Commits MUST use conventional format for the version bump and changelog to work.
REM
REM Format:  type(scope): description
REM
REM   feat:     New feature          -> "Added" in changelog, minor bump
REM   fix:      Bug fix              -> "Fixed" in changelog, patch bump
REM   docs:     Documentation only   -> "Documentation" (no bump)
REM   refactor: Code restructuring   -> "Changed" (no bump)
REM   perf:     Performance          -> "Performance"
REM   test:     Adding/fixing tests  -> "Testing" (no bump)
REM   ci:       CI/CD changes        -> "CI/CD" (no bump)
REM   chore:    Maintenance          -> (skipped in changelog)
REM
REM   Examples:
REM     feat(tools): add a check_links tool
REM     fix(lint): stop the domain/system search at the project root
REM -----------------------------------------------------------------------

REM Always operate on THIS repo, never on whatever directory the caller is standing in.
cd /d "%~dp0"

REM Choose the Python deliberately, never whatever `python` is first on PATH: this repo's venv
REM first (it has the server, Core and OLC installed), then PATH.
set "PY=python"
if exist "%~dp0.venv\Scripts\python.exe" set "PY=%~dp0.venv\Scripts\python.exe"
echo   Python: %PY%

echo.
echo ======================================================
echo   LakeLogic MCP Release
echo ======================================================
echo   Repo: %CD%
echo ======================================================

REM Step 0: Tests - abort the release if they fail
echo.
echo [0/5] Running tests...
"%PY%" -m pytest tests/ -x -q --tb=short
if errorlevel 1 (
    echo.
    echo ERROR: Tests failed. Fix them before releasing.
    exit /b 1
)

REM Step 0a: Docs build - a broken link or page fails the release. Skipped (not failed) when
REM mkdocs is not installed, and it says so: "did not run" must never look like "passed".
echo.
echo [0a/5] Building the docs site...
"%PY%" -c "import mkdocs" 2>NUL
if errorlevel 1 (
    echo   SKIPPED: mkdocs not installed - pip install -r docs-requirements.txt
) else (
    "%PY%" -m mkdocs build --strict -q
    if errorlevel 1 (
        echo.
        echo ERROR: The docs site did not build. Fix it before releasing.
        exit /b 1
    )
)

REM Step 1: Bump version (creates tag + bump commit)
echo.
echo [1/5] Bumping version...
REM Through uvx, so commitizen needs no install in this repo's venv.
if "%1"=="" (
    uvx --from commitizen cz bump --yes
) else (
    uvx --from commitizen cz bump --increment %1 --yes
)
set "BUMP_RC=%ERRORLEVEL%"

REM cz exit code 21 = nothing to bump: only docs/style/refactor/chore/test commits since the
REM last tag. Not a failure - there is simply nothing to release. Push those commits directly.
if "%BUMP_RC%"=="21" (
    echo.
    echo Nothing to release: no feat/fix commits since the last tag.
    echo   Those commits are fine -- just push them:  git push
    echo.
    exit /b 0
)
if not "%BUMP_RC%"=="0" (
    echo.
    echo ERROR: cz bump failed ^(exit %BUMP_RC%^).
    echo   Common cause: commits not in conventional format ^(feat:/fix: prefixes^).
    echo   Check with: git log --oneline
    exit /b 1
)

for /f "tokens=*" %%i in ('git describe --tags --abbrev^=0') do set NEW_TAG=%%i
echo   Tag: %NEW_TAG%

REM Step 2: Generate changelog
echo.
echo [2/5] Generating changelog with git-cliff...
git cliff -o CHANGELOG.md
if errorlevel 1 (
    echo ERROR: git cliff failed. Is git-cliff installed? Run: winget install git-cliff
    exit /b 1
)

REM Step 3: Amend the bump commit to include the changelog
echo.
echo [3/5] Amending bump commit with changelog...
git add CHANGELOG.md
git commit --amend --no-edit

REM Step 4: Re-attach the tag to the amended commit. ANNOTATED (-a): `git push --follow-tags`
REM only pushes annotated tags, so a lightweight tag would never reach GitHub and publish.yml
REM would not run.
echo.
echo [4/5] Re-tagging %NEW_TAG% on amended commit...
git tag -f -a %NEW_TAG% -m "release %NEW_TAG%"

REM Step 5: Push
echo.
echo [5/5] Pushing to GitHub...
git push --force --follow-tags

echo.
echo ======================================================
echo   Release %NEW_TAG% complete!
echo ======================================================
echo.
echo   GitHub Actions now: publish.yml (tests + PyPI), then registry.yml (MCP Registry).
echo   Watch: https://github.com/LakeLogic/lakelogic-mcp/actions
echo.

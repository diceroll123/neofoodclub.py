# List all available commands
default:
    @just --list

# Clean all build artifacts
clean:
    cargo clean || true
    cd neofoodclub_rs && cargo clean || true
    rm -rf dist/
    rm -rf build/
    rm -rf neofoodclub.egg-info/
    rm -rf .pytest_cache/
    rm -rf .coverage
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type f -name "*.so" -delete 2>/dev/null || true
    find . -type f -name "*.pyd" -delete 2>/dev/null || true

# Build the Rust extension in debug mode
build:
    uv run maturin develop

# Build the Rust extension in release mode
build-release:
    uv run maturin develop --release

# Clean and rebuild in debug mode
rebuild: clean build

# Clean and rebuild in release mode
rebuild-release: clean build-release

# Install in development mode (alias for build)
dev: build

# Run Python tests
test:
    uv run pytest tests/

# Run Python tests with coverage
test-coverage:
    uv run pytest --cov=neofoodclub --cov-report=term-missing tests/

# Run Rust tests
test-rust:
    cargo test

# Run Rust tests in the neofoodclub_rs subproject
test-rust-lib:
    cd neofoodclub_rs && cargo test

# Run Rust coverage (requires cargo-llvm-cov: cargo install cargo-llvm-cov)
coverage-rust:
    cargo llvm-cov --all-features --workspace

# Run Rust coverage with HTML report
coverage-rust-html:
    cargo llvm-cov --all-features --workspace --html
    @echo "Coverage report generated at target/llvm-cov/html/index.html"

# Run Rust coverage for neofoodclub_rs subproject
coverage-rust-lib:
    cd neofoodclub_rs && cargo llvm-cov --all-features --workspace

# Run Rust coverage for neofoodclub_rs with HTML report
coverage-rust-lib-html:
    cd neofoodclub_rs && cargo llvm-cov --all-features --workspace --html
    @echo "Coverage report generated at neofoodclub_rs/target/llvm-cov/html/index.html"

# Run Rust coverage and output lcov file
coverage-rust-lcov:
    cargo llvm-cov --all-features --workspace --lcov --output-path lcov.info
    @echo "LCOV report generated at lcov.info"

# Run Rust coverage and output JSON file (best for AI analysis)
coverage-rust-json:
    cargo llvm-cov --all-features --workspace --json --output-path coverage.json
    @echo "JSON coverage report generated at coverage.json"

# Run all tests (Python and Rust)
test-all: rebuild test test-rust test-rust-lib

# Check Rust code without building
check:
    cargo check
    cd neofoodclub_rs && cargo check

# Format Rust code
fmt-rust:
    cargo fmt
    cd neofoodclub_rs && cargo fmt

# Format Python code
fmt-python:
    ruff format .

# Format all code (Python and Rust)
fmt: fmt-rust fmt-python

# Lint Rust code
lint-rust:
    cargo clippy -- -D warnings
    cd neofoodclub_rs && cargo clippy -- -D warnings

# Lint Python code
lint-python:
    ruff check .

# Lint all code (Python and Rust)
lint: lint-rust lint-python

# Build distribution packages
dist:
    uv run maturin build --release

# Build and publish to PyPI (requires credentials)
publish:
    uv run maturin publish

# Run the example
example:
    python examples/max_ter_example.py

# Full CI-like check: format, lint, test
ci: fmt lint test-all

# Watch and rebuild on file changes (requires cargo-watch)
watch:
    cargo watch -x "build" -s "uv run maturin develop"

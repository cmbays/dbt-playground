# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Leaned the repo down to the dbt project. Removed the agent-experiment
  tooling (playgrounds, kanban, multi-agent orchestration, PM workflow,
  observability, debug-session persistence, agent memory) and the
  agent-experiment documentation, leaving a focused Synthea healthcare
  dbt project on DuckDB that serves as the public fixture source and
  dogfood target for the `cute-dbt` tool.

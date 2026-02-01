# Readiness Check Skill

> **Status**: Placeholder - Implementation pending

## Purpose

Capability gap analysis skill for proactive identification of knowledge or tool gaps before committing to work.

## Planned Features

- [ ] Analyze requested work against current capabilities
- [ ] Identify knowledge gaps requiring research
- [ ] Identify tool gaps requiring installation/configuration
- [ ] Integrate with Supervisor for automatic pre-work assessment
- [ ] Trigger research/upskill workflow when gaps found

## Usage (Planned)

```
/readiness-check <task-description>
```

## Integration Points

- Supervisor agent (auto-invoke before work commitment)
- Research workflow (when knowledge gaps found)
- Tool installation workflow (when tool gaps found)

# memory/

```
├── YYYY-MM-DD.md     # Daily: 3-4 bullets (~80 tokens)
├── stats.json        # Access tracking, priorities, lastAccessed
├── projects/        # One-liner per project
├── people/         # Key facts only
└── signals/        # Brief patterns
```

## Auto-Load Priority

On session start:
1. **Always:** Today + Yesterday daily notes
2. **High-priority (score >3):** Frequently accessed files
3. **Context-match:** Files matching session keywords
4. **On-query:** Everything else

## Stats (memory/stats.json)

- `accesses`: file → count
- `recalled`: file → explicit recall count
- `lastAccessed`: file → ISO date
- `missed`: failed recalls → auto-added next maintenance

Priority: `(accesses × 1) + (recalled × 2) - (daysSince × 0.1)`

## Signal Template

```markdown
# 2026-02
- User active on weekends
- Prefers short responses
```

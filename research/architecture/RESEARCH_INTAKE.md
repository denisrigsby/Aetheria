# Research intake (required for every proposal)

Copy and answer before implementing:

1. Which Aetheria capability id does this support?
2. Which failure or limitation does it address?
3. What is the smallest local experiment?
4. What metric can demonstrate improvement (not only aggregate score)?
5. What new authority or risk does it introduce?
6. What is the rollback or removal plan?
7. Which boundary owns it? (`research` | `control_plane` | `production`) — exactly one.
8. Is it allowed under the current authorization scope?
9. Does it require a new benchmark task (visible vs held-out)?
10. Does it require model calls or external access? (Default: **neither**.)

If (7) is `production`, stop. Production receives only manually reviewed, separately certified changes.

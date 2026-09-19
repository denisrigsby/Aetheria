# Public vs mock vs private (overlay)

Use with [ARCHITECTURE.md](ARCHITECTURE.md).

```mermaid
flowchart LR
  subgraph public [Public in this repo]
    CLI[CLI / plant_control]
    UI[Talk-face reference mouth]
    SUP[Supervisor]
    WD[Watchdog]
    MEAS[measurements state]
    MOCK[Mock / reference worker]
  end
  subgraph private [Deliberately private]
    FORGE[Forge console]
    REAL[Real cycle body]
    LIV[Living memory]
  end

  CLI --> SUP
  UI -.->|optional mouth| SUP
  WD -->|relaunch| SUP
  SUP --> MOCK
  SUP --> MEAS
  CLI -->|STOP| SUP
  FORGE -.-> REAL
  REAL -.-> LIV
```

| Piece | Shipping status |
|-------|-----------------|
| Supervisor / watchdog / STOP / heartbeat files | **Public, real** |
| Talk-face reference mouth | **Public, mock spine** |
| Continuity demo pulse | **Public, mock** |
| Forge + living memory + real cycle body | **Private local install** |

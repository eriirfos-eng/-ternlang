mkdir -p edge relay audit

cat > edge/index.md << 'MD'
---
layout: page
title: /edge
---

# /edge
Tier-0 heartbeat edge.  
Put detector code, timing specs, and low-latency notes here.

[← back to root](/)
MD

cat > relay/index.md << 'MD'
---
layout: page
title: /relay
---

# /relay
PSAP relay mock.  
Protobuf schemas, dispatch pipeline docs, and integration tests belong here.

[← back to root](/)
MD

cat > audit/index.md << 'MD'
---
layout: page
title: /audit
---

# /audit
Merkle audit chain + compliance logs.  
Drop audit schema, logs, DPIA skeletons, and verification flows here.

[← back to root](/)
MD

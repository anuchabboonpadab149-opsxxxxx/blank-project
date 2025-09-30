Bigo Agent Top-up (No Payment) - MVP

Overview
- Simple form for customers to create a diamond top-up order (no price, no payment).
- Agent dashboard to assign and mark fulfillment success/failed after manually topping-up via bigo.tv.
- In-memory storage (orders reset on server restart).

Run locally
1) Install Node.js 18+
2) Install dependencies:
   npm install
3) Start the server:
   npm start
4) Open:
   - Customer form: http://localhost:3000/
   - Agent dashboard: http://localhost:3000/agent

Flow
- Customer: choose package or custom amount, enter Bigo ID (digits), submit.
- System: creates order with status QUEUED.
- Agent: open /agent, click "รับงาน", open bigo.tv and top-up manually, mark "สำเร็จ" or "ล้มเหลว".
- Customer: track status via /order/:id.

Notes
- This MVP uses in-memory data for simplicity; integrate a real database (PostgreSQL/MySQL) for production.
- No payment integration per requirement.
- No authentication is included; add RBAC for real deployment.
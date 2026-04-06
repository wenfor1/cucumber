import React, { useState } from 'react';

function App() {
  const [count, setCount] = useState(0);

  return (
    <div style={{ fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Arial", padding: 16 }}>
      <h1 style={{ margin: "0 0 12px" }}>Counter</h1>
      <div style={{ fontSize: 48, fontWeight: 700, marginBottom: 12 }}>{count}</div>
      <div style={{ display: "flex", gap: 8 }}>
        {/* Використовуємо логіку з твого файлу */}
        <button onClick={() => setCount((c) => c - 1)}>-</button>
        <button onClick={() => setCount((c) => c + 1)}>+</button>
        <button onClick={() => setCount(0)}>Reset</button>
      </div>
    </div>
  );
}

export default App;
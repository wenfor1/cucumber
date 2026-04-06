import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  // Створюємо змінну стану 'count', яка початково дорівнює 0
  const [count, setCount] = useState(0);

  return (
    <div className="container mt-5 text-center">
      <div className="p-5 mb-4 bg-light rounded-3 shadow">
        <h1 className="display-4 text-primary">Мій перший React Каунтер</h1>
        <p className="fs-3 mt-4">Поточне значення: <strong>{count}</strong></p>
        
        <div className="mt-4">
          <button 
            className="btn btn-success btn-lg me-2" 
            onClick={() => setCount(count + 1)}
          >
            Збільшити (+)
          </button>
          
          <button 
            className="btn btn-danger btn-lg" 
            onClick={() => setCount(count - 1)}
          >
            Зменшити (-)
          </button>
        </div>

        <button 
          className="btn btn-outline-secondary mt-3" 
          onClick={() => setCount(0)}
        >
          Скинути
        </button>
      </div>
    </div>
  );
}

export default App;
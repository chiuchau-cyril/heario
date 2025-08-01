import React from 'react';
import NewsList from './components/NewsList';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Heario AI 新聞播報</h1>
        <p>AI 驅動的個人新聞站台</p>
      </header>
      <main>
        <NewsList />
      </main>
    </div>
  );
}

export default App;

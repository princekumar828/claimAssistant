import React, { useState } from 'react';
import Chat from './components/Chat';

function App() {
    return (
        <div className="min-h-screen flex flex-col">
            <header className="bg-blue-800 text-white p-4 shadow-md">
                <div className="container mx-auto flex justify-between items-center">
                    <h1 className="text-xl font-bold">RAG Claims Assistant</h1>
                    <span className="text-sm opacity-80">Connected to Local/Mock LLM</span>
                </div>
            </header>
            <main className="flex-1 container mx-auto p-4">
                <Chat />
            </main>
        </div>
    );
}

export default App;

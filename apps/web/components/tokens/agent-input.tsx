'use client';

import React, { useState } from 'react';

const AgentInput = () => {
  const [text, setText] = useState<string>('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();

    setText(e.target.value);
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setText('');
  };

  return (
    <div className="border-b-0 border-b-active-dark full focus-within:border-accent-dark/60 px-2 center gap-4">
      <form className="w-full center gap-2" onSubmit={handleSubmit}>
        <p className="text-accent-dark font-bold">&gt;</p>
        <input
          type="text"
          value={text}
          onChange={handleInputChange}
          placeholder=" Send instructions to agent"
          className="full border-none outline-none ring-0 text-lg font-mono font-medium placeholder:font-semibold"
        />
      </form>
    </div>
  );
};

export default AgentInput;

# utils\nextBuilder\frontend\ai\components\ai_ui_component.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_component  # nopep8

FLEX_GPT_TEMPLATE = """'use client'
import { useState, useEffect, useRef } from 'react';

export default function Tiny() {
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [includeConversation, setIncludeConversation] = useState(false);
  const [buttonIcon, setButtonIcon] = useState('→');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingChar, setLoadingChar] = useState('/');

  const [selectedModel, setSelectedModel] = useState('general'); // default selection
  const models = [
    'rag', 'ragmem', 'memory', 'chain', 'general',
    // 'transformaer'
  ];
  const [expandedCodeSegments, setExpandedCodeSegments] = useState({});

  const [memory, setMemory] = useState('next-flex');
  const [type, setType] = useState('uncensored');

  const messageInputRef = useRef(null);

  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);

  const [showEmptyMessageWarning, setShowEmptyMessageWarning] = useState(false);

  const [codeSnippets, setCodeSnippets] = useState([]);
  const [currentSlide, setCurrentSlide] = useState(0);

  const [activeScreen, setActiveScreen] = useState('chat');

  const [sliderIndex, setSliderIndex] = useState(0);

  const showChatScreen = () => {
    setActiveScreen('chat');
  };

  const sliderContainerStyle = {
    display: 'flex',
    width: '200%', // for two sections
    transform: `translateX(${sliderIndex === 0 ? '0' : '-50%'})`,
    transition: 'transform 0.3s ease-out'
  };

  const showCodeScreen = () => {
    setActiveScreen('code');
  };

  const handleModelChange = (e) => {
    setSelectedModel(e.target.value);
  };

  const goToNextSlide = () => {
    setCurrentSlide((prevSlide) => (prevSlide + 1) % codeSnippets.length);
  };

  const goToPreviousSlide = () => {
    setCurrentSlide((prevSlide) => {
      return prevSlide === 0 ? codeSnippets.length - 1 : prevSlide - 1;
    });
  };

  useEffect(() => {
    let intervalId;

    if (isLoading) {
      const chars = [":''", "'':", "..:", ":.."];
      let charIndex = 0;

      intervalId = setInterval(() => {
        setLoadingChar(chars[charIndex]);
        charIndex = (charIndex + 1) % chars.length;
      }, 250); // Change character every 250ms
    } else {
      setLoadingChar(":''");
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Check if the message is empty
    if (message.trim() === '') {
      setShowEmptyMessageWarning(true); // Show warning message
      return; // Exit the function early
    }

    setIsLoading(true);
    setShowEmptyMessageWarning(false); // Hide warning if previously shown

    // Check if the last message in the conversation is already a "Sending..." message
    const isLastMessageSending = conversation.length > 0 && conversation[conversation.length - 1].isLoading;

    // Only add a new "Sending..." message if there isn't one already
    if (!isLastMessageSending) {
      setConversation(prev => [...prev, { label: "User", text: message, sender: 'user', isLoading: true }]);
    }

    const lastTenMessages = conversation.slice(Math.max(conversation.length - 10, 0));
    
    const filteredMessages = lastTenMessages.filter(msg => msg.text.trim() !== "User:");
    const filteredMessages0 = filteredMessages.filter(msg => msg.text.trim() !== "FlexGPT:");

    let fullMessage;

    const conversationText = filteredMessages0.map(c => `${c.label}: ${c.text}`).join('\\n');
    fullMessage = `${conversationText}\\nUser: ${message}`;

    try {
      // console.log(fullMessage)
      const res = await fetch('/api/inference', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: fullMessage,
          type: type,
          model: selectedModel,
          folder: 'next-flex-data',
          memory: memory
        }),
      });
      const data = await res.json();
      // console.log(data);

      

      setConversation(prev => [
        ...prev.slice(0, -1), // Remove the last item (placeholder)
        { label: "User", text: message, sender: 'user' },
        {
          label: "FlexGPT", text: data["choices"][0]["message"]["content"], sender: 'ai'
        }
      ]);

      if (messageInputRef.current) {
        messageInputRef.current.style.height = 'inherit';
      }

    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
      setMessage('');
    }
  };

  const handleInput = (e) => {
    setMessage(e.target.value);
    if (showEmptyMessageWarning && e.target.value.trim() !== '') {
      setShowEmptyMessageWarning(false);
    }
    e.target.style.height = 'inherit';
    e.target.style.height = `${e.target.scrollHeight}px`;
    const numberOfLines = (e.target.scrollHeight - e.target.clientHeight) / parseInt(window.getComputedStyle(e.target).lineHeight);
    setButtonIcon(numberOfLines > 4 ? '↑' : '→');
  };

  const splitMessage = (text) => {
    const codeBlockRegex = /```[\s\S]*?```/g;
    let segments = [];
    let lastIndex = 0;

    text.replace(codeBlockRegex, (match, index) => {
      segments.push(text.slice(lastIndex, index)); // Push the text before the code block
      segments.push(match); // Push the code block
      lastIndex = index + match.length;
    });

    if (lastIndex < text.length) {
      segments.push(text.slice(lastIndex)); // Push the remaining text
    }

    return segments;
  };

  const handleCodeButtonClick = (e, codeSegment) => {
    e.preventDefault();
    setCodeSnippets(prevSnippets => [...prevSnippets, codeSegment]);
    // Handle the button click event
    // For example, you might want to execute the code or display it in a modal
    // console.log("Code to execute:", codeSegment);
  };

  const toggleCodeSegment = (index) => {
    setExpandedCodeSegments(prevState => ({
      ...prevState,
      [index]: !prevState[index]
    }));
  };

  const formatSegment = (segment, index) => {
    // ... existing conditions ...
    if (segment.startsWith("```") && segment.endsWith("```")) {
      return (
        <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '1rem 0' }}>
          {expandedCodeSegments[index] && (
            <pre style={{ flexGrow: 1, marginRight: '10px' }}><code>{segment.slice(3, -3)}</code></pre>
          )}
          <button onClick={() => handleCodeExtract(index)}>Extract Code</button>
        </div>
      );
    }

    if (segment.startsWith("```") && segment.endsWith("```")) {
      return (
        <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '1rem 0' }}>
          {expandedCodeSegments[index] && (
            <pre style={{ flexGrow: 1, marginRight: '10px' }}><code>{segment.slice(3, -3)}</code></pre>
          )}
          <button onClick={(e) => handleCodeButtonClick(e, segment)}>Extract Code</button>
        </div>
      );
    }

    if (segment.isLoading) {
      return <p key={segment.label + segment.text} style={{ margin: '0.5rem 0' }}>Sending...</p>;
    }

    if (segment.startsWith("```") && segment.endsWith("```")) {
      return (
        <div key={index} style={{ margin: '1rem 0', display: 'flex', alignItems: 'center' }}>
          <pre style={{ marginRight: '10px' }}><code>{segment.slice(3, -3)}</code></pre>
          <button onClick={() => handleCodeButtonClick(segment)}>Extract Code</button>
        </div>
      );
    }

    return segment.split('\\n').map((line, lineIndex) => (
      <p key={lineIndex} style={{ margin: '0.5rem 0' }}>
        {line}
      </p>
    ));
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // Prevent the default action to avoid adding a new line
      handleSubmit(e); // Call the handleSubmit function
    }
  };


  const showLeft = () => {
    setSliderIndex(0);
  };

  const showRight = () => {
    setSliderIndex(1);
  };

  const handleCodeExtract = (index) => {
    setCurrentSlide(index);
    // Optional: Trigger download
    const code = codeSnippets[index];
    const filename = `extracted_code_${index}.txt`;
    downloadCode(code, filename); // This assumes you have a function to handle downloads
  };

  const downloadCode = (code, filename) => {
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(code));
    element.setAttribute('download', filename);
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div>
      
      {/* Slider Container */}
      <div style={sliderContainerStyle}>
        {/* Chat Form Section */}
        <div style={{ flex: 1, width: '50%', minHeight: '80vh', display: 'flex', justifyContent: 'center', flexDirection: 'column', alignItems: 'center' }}>
          {/* ... Chat form content ... */}

          <form onSubmit={handleSubmit} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4" style={{ width: '80vw', maxHeight: '80vh', overflowY: 'auto', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>

            <div className="text-1xl mb-6 text-black" style={{ overflowY: 'auto' }}>
              {conversation.map((message, index) => (
                <div key={index}>
                  <p className={message.sender === 'user' ? 'text-blue-500 font-bold' : 'text-green-600 font-bold'}>{message.label}:</p>
                  {message.isLoading ? <p>Sending...</p> : splitMessage(message.text).map((segment, i) => formatSegment(segment, i))}
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between mb-4">
              {/* Textarea */}
              <textarea
                ref={messageInputRef}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="message"
                placeholder="Message"
                value={message}
                onChange={handleInput}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
                style={{ overflowY: 'auto', maxHeight: '30vh', marginRight: '10px' }} // Add a margin to the right of the textarea
              />

              {/* Warning Message for Empty Input */}
              {showEmptyMessageWarning && (
                <div style={{ color: 'red', marginTop: '10px' }}>
                  Please enter a message before sending.
                </div>
              )}

              {/* Send Button */}
              <button
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                type="submit"
                disabled={isLoading}
              >
                {isLoading ? loadingChar : buttonIcon}
              </button>
            </div>

          </form>

          {/* <div className="fixed bottom-0 left-0 w-full bg-gray-200 p-4">
            <label className="flex items-center justify-between">
              <span className="mr-2 text-black">Include Entire Conversation:</span>
              <input
                type="checkbox"
                checked={includeConversation}
                onChange={() => setIncludeConversation(!includeConversation)}
              />
            </label>
          </div> */}

        </div>

        {/* Code Snippet Section */}
        <div style={{ flex: 1, width: '80vw', minHeight: '80vh', display: 'flex', justifyContent: 'center', flexDirection: 'column', alignItems: 'center' }}>
          {/* ... Code snippet content ... */}
          {codeSnippets.length > 0 && (
            <div>
              <button onClick={goToPreviousSlide}>Previous</button>
              <pre><code>{codeSnippets[currentSlide]}</code></pre>
              {/* Add a button to extract the current code snippet */}
              <button onClick={() => handleCodeExtract(currentSlide)}>Extract Code</button>
            </div>
          )}
        </div>


      </div>
<div className="navigation-buttons-container" style={{ display: 'flex', justifyContent: 'center', margin: '20px 0' }}>
  <button onClick={showLeft} style={{ marginRight: '10px' }}>Show Chat</button>
  <button onClick={showRight}>Show Code Snippets</button>
</div>

    </div>
  );

}
"""


create_component('AIComponent', FLEX_GPT_TEMPLATE)

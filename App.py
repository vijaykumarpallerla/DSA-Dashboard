import os
import json
from datetime import datetime, date
from flask import Flask, url_for, session, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
load_dotenv()

# --- HTML, CSS, and JavaScript Embedded as a Single String ---
LOGIN_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DSA Dashboard - Login</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-bg: #0f0f23; --secondary-bg: #1a1a3a; --card-bg: #2d2d5f;
            --text-color: #00d4ff; --white-color: #ffffff; --accent-color: #00d4ff;
            --interactive-purple: #7c3aed; --interactive-pink: #ec4899; --interactive-green: #10b981;
            --interactive-orange: #f59e0b; --glow-blue: #3b82f6; --dark-accent: #111827;
            --font-family: 'Poppins', sans-serif;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: var(--font-family); 
            background: linear-gradient(135deg, var(--primary-bg), var(--secondary-bg)); 
            color: var(--white-color); 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        
        /* Background Animation */
        .bg-animation {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: -1;
        }
        .bg-animation::before {
            content: '';
            position: absolute;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(0, 212, 255, 0.15), rgba(124, 58, 237, 0.1), transparent);
            animation: rotate 20s linear infinite;
        }
        @keyframes rotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .login-container {
            background: rgba(45, 45, 95, 0.9);
            border-radius: 20px;
            padding: 3rem 2.5rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(0, 212, 255, 0.3);
            text-align: center;
            max-width: 450px;
            width: 90%;
            position: relative;
        }
        
        .logo {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-color), var(--interactive-purple), var(--interactive-pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
        }
        
        .subtitle {
            font-size: 1.1rem;
            color: #b0b3c7;
            margin-bottom: 2.5rem;
            font-weight: 300;
        }
        
        .google-login-btn {
            background: linear-gradient(135deg, #4285f4, #34a853);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            width: 100%;
            text-decoration: none;
            margin-bottom: 1.5rem;
        }
        
        .google-login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(66, 133, 244, 0.4);
        }
        
        .google-icon {
            width: 20px;
            height: 20px;
            background: white;
            border-radius: 3px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .features {
            text-align: left;
            margin-top: 2rem;
        }
        
        .feature-item {
            display: flex;
            align-items: center;
            margin-bottom: 0.8rem;
            color: #b0b3c7;
            font-size: 0.9rem;
        }
        
        .feature-icon {
            color: var(--interactive-green);
            margin-right: 10px;
            font-weight: bold;
        }
        
        @media (max-width: 480px) {
            .login-container {
                padding: 2rem 1.5rem;
                margin: 1rem;
            }
            .logo {
                font-size: 2.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="bg-animation"></div>
    
    <div class="login-container">
        <div class="logo">DSA Dashboard</div>
        <p class="subtitle">Master Data Structures & Algorithms with AI-powered learning</p>
        
        <a href="/oauth-login" class="google-login-btn">
            <div class="google-icon">G</div>
            Continue with Google
        </a>
        
        <div class="features">
            <div class="feature-item">
                <span class="feature-icon">✓</span>
                <span>Interactive practice questions</span>
            </div>
            <div class="feature-item">
                <span class="feature-icon">✓</span>
                <span>AI-powered explanations</span>
            </div>
            <div class="feature-item">
                <span class="feature-icon">✓</span>
                <span>Progress tracking & streaks</span>
            </div>
            <div class="feature-item">
                <span class="feature-icon">✓</span>
                <span>Comprehensive DSA curriculum</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

HTML_TEMPLATE_WITH_ASSETS = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DSA Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-bg: #0f0f23; --secondary-bg: #1a1a3a; --card-bg: #2d2d5f;
            --text-color: #00d4ff; --white-color: #ffffff; --accent-color: #00d4ff;
            --interactive-purple: #7c3aed; --interactive-pink: #ec4899; --interactive-green: #10b981;
            --interactive-orange: #f59e0b; --glow-blue: #3b82f6; --dark-accent: #111827;
            --font-family: 'Poppins', sans-serif;
        }
        * { box-sizing: border-box; }
        body { 
            font-family: var(--font-family); 
            background: linear-gradient(135deg, var(--primary-bg), var(--secondary-bg)); 
            color: var(--white-color); 
            margin: 0; 
            display: flex; 
            overflow-x: hidden; 
            position: relative;
        }
        
        /* Background Animation for main page */
        .main-bg-animation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: -1;
            pointer-events: none;
        }
        .main-bg-animation::before {
            content: '';
            position: absolute;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(0, 212, 255, 0.08), rgba(124, 58, 237, 0.05), transparent);
            animation: rotate 25s linear infinite;
        }
        @keyframes rotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .sidebar { width: 260px; background-color: var(--secondary-bg); padding: 20px; height: 100vh; position: fixed; left: 0; top: 0; transition: transform 0.3s ease; z-index: 1000; }
        .sidebar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .sidebar-header h3 { color: var(--accent-color); margin: 0; }
        .close-btn { display: none; font-size: 24px; cursor: pointer; }
        #syllabus-list { list-style: none; padding: 0; }
        #syllabus-list li { padding: 12px; margin-bottom: 8px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; transition: background-color 0.2s; }
        #syllabus-list li:hover { background-color: var(--card-bg); }
        #syllabus-list li.active { background-color: var(--accent-color); color: var(--white-color); }
        .syllabus-checkbox { margin-right: 12px; width: 18px; height: 18px; cursor: pointer; accent-color: var(--accent-color); }
        .main-content { margin-left: 260px; padding: 20px; width: calc(100% - 260px); transition: margin-left 0.3s ease; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .user-profile { display: flex; align-items: center; }
        .header-buttons { display: flex; align-items: center; gap: 15px; }
        .submissions-button { 
            color: var(--white-color); 
            background: linear-gradient(135deg, var(--interactive-green), var(--glow-blue)); 
            padding: 10px 20px; 
            border-radius: 25px; 
            border: none;
            font-size: 14px; 
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease; 
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        }
        .submissions-button:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5); 
        }
        #user-picture { width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; }
        .logout-button { 
            color: var(--white-color); 
            background: linear-gradient(135deg, var(--interactive-orange), var(--interactive-pink)); 
            padding: 10px 20px; 
            border-radius: 25px; 
            text-decoration: none; 
            font-size: 14px; 
            font-weight: 600;
            transition: all 0.3s ease; 
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
        }
        .logout-button:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 8px 25px rgba(245, 158, 11, 0.5); 
        }
        .logout-button:hover { background-color: var(--accent-color); }
        .lobby { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .widget { background-color: var(--secondary-bg); padding: 20px; border-radius: 10px; text-align: center; }
        .widget h4 { margin-top: 0; color: var(--accent-color); font-weight: 400; }
        .widget p { font-size: 2em; font-weight: 600; margin: 10px 0 0 0; }
        .overall-progress { background-color: var(--secondary-bg); padding: 20px; border-radius: 10px; margin-bottom: 30px; }
        .progress-bar-container { width: 100%; background-color: var(--card-bg); border-radius: 20px; height: 20px; margin: 10px 0; }
        .progress-bar { width: 0%; height: 100%; background: linear-gradient(90deg, var(--interactive-green) 0%, var(--interactive-orange) 100%); border-radius: 20px; transition: width 0.5s ease; }
        .interactive-area { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .view-panel { background-color: var(--secondary-bg); padding: 25px; border-radius: 10px; min-height: 400px; max-height: 60vh; overflow-y: auto; }
        #notes-view h3, #practice-view h3 { color: var(--accent-color); }
        #notes-view code { background-color: #000; padding: 2px 5px; border-radius: 4px; font-family: monospace; }
        #notes-view pre { background-color: #000; padding: 15px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; }
        #practice-content button { 
            background: linear-gradient(135deg, var(--interactive-purple), var(--glow-blue)); 
            color: var(--white-color); 
            border: none; 
            padding: 12px 20px; 
            border-radius: 25px; 
            cursor: pointer; 
            margin: 10px 5px 10px 0; 
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
        }
        #practice-content button:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 8px 25px rgba(124, 58, 237, 0.5);
        }
        #practice-content button:disabled { background-color: #555; cursor: not-allowed;}
        #practice-content textarea { 
            width: 100%; 
            height: 120px; 
            background-color: var(--card-bg); 
            color: var(--white-color); 
            border: 1px solid var(--accent-color); 
            border-radius: 5px; 
            padding: 12px; 
            margin-top: 10px; 
            font-family: var(--font-family);
            font-size: 16px;
            line-height: 1.5;
            resize: vertical;
        }
        #question-counter { 
            background: linear-gradient(135deg, var(--interactive-purple), var(--interactive-pink)); 
            color: var(--white-color); 
            padding: 8px 15px; 
            border-radius: 20px; 
            font-weight: 600; 
            margin-bottom: 15px; 
            display: inline-block;
        }
        #question-buttons { 
            display: flex; 
            gap: 10px; 
            margin-top: 15px; 
            flex-wrap: wrap;
        }
        #result-area { 
            margin-top: 15px; 
            padding: 15px; 
            border-radius: 10px; 
            font-weight: 600;
        }
        #result-area.correct { 
            background: linear-gradient(135deg, var(--interactive-green), rgba(16, 185, 129, 0.3)); 
            color: var(--white-color);
        }
        #result-area.incorrect { 
            background: linear-gradient(135deg, var(--interactive-orange), rgba(245, 158, 11, 0.3)); 
            color: var(--white-color);
        }
        #review-area { margin-top: 15px; padding: 10px; border-radius: 5px; background-color: var(--card-bg); }
        
        /* AI Assistant Circular Button */
        .ai-button { 
            position: fixed; 
            bottom: 20px; 
            right: 20px; 
            width: 60px; 
            height: 60px; 
            background: linear-gradient(135deg, var(--interactive-purple), var(--interactive-pink)); 
            border-radius: 50%; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            cursor: pointer; 
            box-shadow: 0 4px 20px rgba(124, 58, 237, 0.6); 
            z-index: 1002; 
            transition: all 0.3s ease; 
            border: none;
            font-family: var(--font-family);
            font-weight: 600;
            animation: pulseGlow 2s infinite;
        }
        @keyframes pulseGlow {
            0%, 100% { 
                box-shadow: 0 4px 20px rgba(124, 58, 237, 0.6); 
                transform: scale(1);
            }
            50% { 
                box-shadow: 0 8px 30px rgba(124, 58, 237, 0.9); 
                transform: scale(1.05);
            }
        }
        .ai-button .ai-icon {
            font-size: 20px;
            color: var(--white-color);
        }
        .ai-button:hover { 
            transform: scale(1.1); 
            box-shadow: 0 8px 35px rgba(124, 58, 237, 0.8); 
        }
        
        /* AI Chat Popup */
        .chat-popup { 
            position: fixed; 
            bottom: 90px; 
            right: 20px; 
            width: 450px; 
            height: 600px; 
            background-color: var(--secondary-bg); 
            border-radius: 15px; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.3); 
            z-index: 1001; 
            display: none; 
            flex-direction: column; 
            overflow: hidden;
            animation: slideUp 0.3s ease;
            touch-action: none; /* Prevent touch scrolling on mobile */
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .chat-popup.show { display: flex; }
        
        .chat-header { 
            background: linear-gradient(135deg, var(--interactive-purple), var(--interactive-pink)); 
            padding: 15px; 
            color: var(--white-color); 
            font-weight: 600; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
        }
        .chat-close { 
            cursor: pointer; 
            font-size: 20px; 
            font-weight: bold; 
            width: 25px; 
            height: 25px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            border-radius: 50%; 
            background-color: rgba(255,255,255,0.2); 
            transition: background-color 0.2s; 
        }
        .chat-close:hover { background-color: rgba(255,255,255,0.3); }
        .chat-body { 
            flex: 1; 
            display: flex; 
            flex-direction: column; 
            overflow: hidden; /* Ensure proper scrolling containment */
        }
        .chat-messages { 
            flex: 1 1 auto !important; 
            overflow-y: scroll !important; 
            overflow-x: hidden !important;
            padding: 15px !important;
            height: 450px !important; 
            max-height: 450px !important;
            min-height: 450px !important;
            position: relative !important;
            background: transparent !important;
        }
        .chat-messages::-webkit-scrollbar {
            width: 6px;
        }
        .chat-messages::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
        }
        .chat-messages::-webkit-scrollbar-thumb {
            background: var(--accent-color);
            border-radius: 3px;
        }
        .chat-messages::-webkit-scrollbar-thumb:hover {
            background: var(--interactive-purple);
        }
        .message { 
            padding: 10px 15px; 
            border-radius: 18px; 
            max-width: 80%; 
            line-height: 1.4; 
            word-wrap: break-word; 
            word-break: break-word;
            white-space: pre-wrap;
            overflow-wrap: break-word;
            hyphens: auto;
            margin-bottom: 8px; /* Add spacing between messages */
            display: block; /* Ensure proper display */
        }
        .message.user { 
            background: linear-gradient(135deg, var(--glow-blue), var(--interactive-green)); 
            color: var(--white-color); 
            margin-left: auto; /* Push to right side */
            margin-right: 0;
            border-bottom-right-radius: 4px; 
        }
        .message.assistant { 
            background-color: var(--card-bg); 
            color: var(--white-color); 
            margin-left: 0; /* Keep on left side */
            margin-right: auto;
            border-bottom-left-radius: 4px; 
        }
        .chat-input { 
            display: flex; 
            gap: 8px; 
            padding: 15px;
            flex-shrink: 0; /* Prevent input from shrinking */
        }
        #ai-input { 
            flex-grow: 1; 
            background-color: var(--card-bg); 
            border: 2px solid transparent; 
            color: var(--white-color); 
            padding: 12px 15px; 
            border-radius: 25px; 
            outline: none; 
            transition: border-color 0.2s; 
            resize: none;
            overflow-y: auto;
            overflow-x: hidden;
            height: 44px !important; /* Fixed height */
            min-height: 44px !important;
            max-height: 44px !important;
            font-family: var(--font-family);
            font-size: 14px;
            line-height: 1.4;
            word-wrap: break-word;
            white-space: nowrap; /* Prevent line breaks */
        }
        #ai-input:focus { 
            border-color: var(--accent-color); 
        }
        #ai-send-btn { 
            background: linear-gradient(135deg, var(--interactive-orange), var(--interactive-pink)); 
            border: none; 
            color: var(--white-color); 
            padding: 12px 20px; 
            border-radius: 25px; 
            cursor: pointer; 
            font-weight: 600; 
            transition: transform 0.2s; 
        }
        #ai-send-btn:hover { 
            transform: scale(1.05); 
        }
        
        /* Submissions Modal */
        .submissions-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 2000;
        }
        .submissions-modal.show { display: flex; }
        .modal-content {
            background: var(--secondary-bg);
            border-radius: 15px;
            width: 90%;
            max-width: 800px;
            max-height: 80vh;
            overflow: hidden;
            border: 1px solid var(--accent-color);
        }
        .modal-header {
            background: linear-gradient(135deg, var(--interactive-green), var(--glow-blue));
            padding: 20px;
            color: var(--white-color);
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .modal-close {
            font-size: 24px;
            cursor: pointer;
            font-weight: bold;
        }
        .modal-body {
            padding: 20px;
            max-height: 60vh;
            overflow-y: auto;
        }
        .submission-item {
            background: var(--card-bg);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid var(--accent-color);
        }
        .submission-item.correct {
            border-left-color: var(--interactive-green);
        }
        .submission-item.incorrect {
            border-left-color: var(--interactive-orange);
        }
        .submission-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .submission-topic {
            background: var(--accent-color);
            color: var(--white-color);
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 600;
        }
        .submission-status {
            font-weight: 600;
        }
        .submission-status.correct { color: var(--interactive-green); }
        .submission-status.incorrect { color: var(--interactive-orange); }
        .submission-question {
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--accent-color);
        }
        .submission-answer {
            background: rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 8px;
        }
        .submission-time {
            font-size: 12px;
            color: #999;
        }
        
        .hamburger-menu { display: none; position: fixed; top: 15px; left: 15px; font-size: 30px; z-index: 1001; cursor: pointer; background-color: var(--secondary-bg); padding: 5px 10px; border-radius: 5px; }
        @media (max-width: 992px) {
            .sidebar { transform: translateX(-100%); }
            .sidebar.show { transform: translateX(0); }
            .main-content { margin-left: 0; width: 100%; padding: 15px; }
            .hamburger-menu, .close-btn { display: block; }
            .interactive-area { grid-template-columns: 1fr; }
            .chat-popup { 
                width: calc(100% - 40px); 
                height: 500px; 
                bottom: 90px; 
                right: 20px; 
                left: 20px; 
            }
            .ai-button {
                bottom: 15px;
                right: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="main-bg-animation"></div>
    <div class="hamburger-menu" id="hamburger-menu">&#9776;</div>
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h3>DSA Path</h3>
            <span class="close-btn" id="close-btn">&times;</span>
        </div>
        <nav>
            <div id="syllabus-container">
                <h4>Syllabus</h4>
                <ul id="syllabus-list"></ul>
            </div>
        </nav>
    </aside>

    <main class="main-content" id="main-content">
        <header class="header">
            <div class="user-profile">
                <img id="user-picture" src="" alt="User Picture">
                <span id="user-name">Loading...</span>
            </div>
            <div class="header-buttons">
                <button id="submissions-btn" class="submissions-button">📝 Submissions</button>
                <a href="/logout" class="logout-button">&#10148;</a>
            </div>
        </header>

        <section class="lobby">
            <div class="widget"><h4>Today's Progress</h4><p><span id="time-spent">0</span> hours</p></div>
            <div class="widget"><h4>Current Streak</h4><p><span id="current-streak">0</span> days 🔥</p></div>
            <div class="widget"><h4>Highest Streak</h4><p><span id="highest-streak">0</span> days 🏆</p></div>
        </section>

        <section class="overall-progress">
            <h4>Overall Course Progress</h4>
            <div class="progress-bar-container">
                <div class="progress-bar" id="progress-bar"></div>
            </div>
            <span id="progress-percentage">0%</span>
        </section>

        <section class="interactive-area">
            <div id="notes-view" class="view-panel"><h3>Select a topic from the syllabus to see notes.</h3></div>
            <div id="practice-view" class="view-panel">
                <h3>Practice Session</h3>
                <div id="practice-content">
                    <p>Select a topic and click 'Get Question' to start practicing!</p>
                    <button id="get-question-btn" disabled>Get Question</button>
                    <div id="question-area" style="display: none;">
                        <div id="question-counter">
                            <span>Question <span id="current-question-num">1</span></span>
                        </div>
                        <p id="question-text"></p>
                        <textarea id="answer-input" placeholder="Type your answer here..."></textarea>
                        <div id="question-buttons">
                            <button id="submit-answer-btn">Submit Answer</button>
                            <button id="hint-btn">Show Hint</button>
                            <button id="next-question-btn" style="display: none;">Next Question</button>
                        </div>
                        <p id="hint-text" style="display: none;"></p>
                        <div id="result-area" style="display: none;">
                            <p id="result-text"></p>
                        </div>
                        <div id="review-area"></div>
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <!-- AI Assistant -->
    <button class="ai-button" id="ai-button">DSAI</button>
    
    <div class="chat-popup" id="chat-popup">
        <div class="chat-header">
            <span>DSAI Assistant</span>
            <span class="chat-close" id="chat-close">&times;</span>
        </div>
        <div class="chat-body">
            <div class="chat-messages" id="chat-messages">
                <div class="message assistant">Hello! How can I help you with DSA today?</div>
            </div>
            <div class="chat-input">
                <input type="text" id="ai-input" placeholder="Ask a question..." />
                <button id="ai-send-btn">Send</button>
            </div>
        </div>
    </div>

    <!-- Submissions Modal -->
    <div class="submissions-modal" id="submissions-modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>📝 Your Submissions</h3>
                <span class="modal-close" id="submissions-close">&times;</span>
            </div>
            <div class="modal-body" id="submissions-list">
                <p>Loading your submissions...</p>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            let currentUserData = {};
            let selectedTopic = null;
            let currentQuestionNumber = 1;

            const DOMElements = {
                userName: document.getElementById('user-name'), userPicture: document.getElementById('user-picture'),
                timeSpent: document.getElementById('time-spent'), currentStreak: document.getElementById('current-streak'),
                highestStreak: document.getElementById('highest-streak'), progressBar: document.getElementById('progress-bar'),
                progressPercentage: document.getElementById('progress-percentage'), syllabusList: document.getElementById('syllabus-list'),
                notesView: document.getElementById('notes-view'), getQuestionBtn: document.getElementById('get-question-btn'),
                questionArea: document.getElementById('question-area'), questionText: document.getElementById('question-text'),
                answerInput: document.getElementById('answer-input'), submitAnswerBtn: document.getElementById('submit-answer-btn'),
                hintBtn: document.getElementById('hint-btn'), hintText: document.getElementById('hint-text'),
                reviewArea: document.getElementById('review-area'), hamburgerMenu: document.getElementById('hamburger-menu'),
                sidebar: document.getElementById('sidebar'), closeBtn: document.getElementById('close-btn'),
                mainContent: document.getElementById('main-content'), aiButton: document.getElementById('ai-button'),
                chatPopup: document.getElementById('chat-popup'), chatClose: document.getElementById('chat-close'),
                chatMessages: document.getElementById('chat-messages'), aiInput: document.getElementById('ai-input'), 
                aiSendBtn: document.getElementById('ai-send-btn'), currentQuestionNum: document.getElementById('current-question-num'),
                nextQuestionBtn: document.getElementById('next-question-btn'), resultArea: document.getElementById('result-area'),
                resultText: document.getElementById('result-text'), submissionsBtn: document.getElementById('submissions-btn'),
                submissionsModal: document.getElementById('submissions-modal'), submissionsClose: document.getElementById('submissions-close'),
                submissionsList: document.getElementById('submissions-list'),
            };

            // LocalStorage helper functions for persistence
            const storage = {
                setSelectedTopic: (topicName) => localStorage.setItem('selectedTopic', topicName),
                getSelectedTopic: () => localStorage.getItem('selectedTopic'),
                setTopicNotes: (topicName, notes) => localStorage.setItem(`notes_${topicName}`, notes),
                getTopicNotes: (topicName) => localStorage.getItem(`notes_${topicName}`),
                clearSelectedTopic: () => localStorage.removeItem('selectedTopic')
            };

            const api = {
                async fetch(url, options = {}) {
                    try {
                        const response = await fetch(url, options);
                        if (!response.ok) {
                            if (response.status === 401) {
                                // Only redirect to login for authentication errors
                                if (url.startsWith('/api/')) window.location.href = '/login';
                            }
                            
                            // Try to get error details from response
                            let errorData;
                            try {
                                errorData = await response.json();
                            } catch {
                                errorData = { error: `HTTP error! status: ${response.status}` };
                            }
                            
                            // Return error data instead of throwing for 4xx/5xx errors
                            return errorData;
                        }
                        return await response.json();
                    } catch (error) {
                        console.error(`Fetch error for ${url}:`, error);
                        throw error;
                    }
                },
                getUserData: () => api.fetch('/api/user_data'),
                toggleTopic: (topicName) => api.fetch('/api/toggle_topic', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ topic_name: topicName }) }),
                generateNotes: (topic) => api.fetch('/api/generate_notes', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ topic }) }),
                generateQuestion: (topic) => api.fetch('/api/generate_question', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ topic }) }),
                reviewAnswer: (question, answer) => api.fetch('/api/review_answer', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question, answer }) }),
                saveSubmission: (topic, question, answer, isCorrect) => api.fetch('/api/save_submission', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ topic, question, answer, isCorrect }) }),
                getSubmissions: () => api.fetch('/api/get_submissions'),
                askAssistant: (query) => api.fetch('/api/ask_assistant', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query }) }),
            };

            const ui = {
                updateDashboard: () => {
                    const { name, picture, time_spent_today_hours, current_streak, highest_streak, progress_percentage } = currentUserData;
                    DOMElements.userName.textContent = name;
                    DOMElements.userPicture.src = picture;
                    DOMElements.timeSpent.textContent = time_spent_today_hours;
                    DOMElements.currentStreak.textContent = current_streak;
                    DOMElements.highestStreak.textContent = highest_streak;
                    DOMElements.progressPercentage.textContent = `${progress_percentage}%`;
                    DOMElements.progressBar.style.width = `${progress_percentage}%`;
                    ui.renderSyllabus();
                    
                    // Restore selected topic after page refresh
                    const savedTopic = storage.getSelectedTopic();
                    if (savedTopic) {
                        const topicElement = document.querySelector(`#syllabus-list li[data-topic-name="${savedTopic}"]`);
                        if (topicElement) {
                            ui.restoreTopicSelection(savedTopic, topicElement);
                        }
                    }
                },
                renderSyllabus: () => {
                    DOMElements.syllabusList.innerHTML = '';
                    currentUserData.syllabus.forEach(topic => {
                        const li = document.createElement('li');
                        li.dataset.topicName = topic.name;
                        li.innerHTML = `<input type="checkbox" class="syllabus-checkbox" ${topic.completed ? 'checked' : ''}><span>${topic.name}</span>`;
                        DOMElements.syllabusList.appendChild(li);
                    });
                },
                handleTopicSelection: async (topicName, listItem) => {
                    document.querySelectorAll('#syllabus-list li').forEach(el => el.classList.remove('active'));
                    listItem.classList.add('active');
                    selectedTopic = topicName;
                    storage.setSelectedTopic(topicName); // Save to localStorage
                    DOMElements.getQuestionBtn.disabled = false;
                    DOMElements.notesView.innerHTML = `<h3>Loading notes for ${topicName}...</h3>`;
                    try {
                        const data = await api.generateNotes(topicName);
                        const notesHtml = `<h3>Notes for ${topicName}</h3><p>${data.notes.replace(/\\n/g, '<br>')}</p>`;
                        DOMElements.notesView.innerHTML = notesHtml;
                        storage.setTopicNotes(topicName, notesHtml); // Save notes to localStorage
                        const topic = currentUserData.syllabus.find(t => t.name === topicName);
                        if (!topic.completed) {
                            await api.toggleTopic(topicName);
                            loadInitialData();
                        }
                    } catch (error) { DOMElements.notesView.innerHTML = `<h3>Error loading notes. Please try again.</h3>`; }
                },
                restoreTopicSelection: (topicName, listItem) => {
                    document.querySelectorAll('#syllabus-list li').forEach(el => el.classList.remove('active'));
                    listItem.classList.add('active');
                    selectedTopic = topicName;
                    DOMElements.getQuestionBtn.disabled = false;
                    
                    // Try to restore notes from localStorage first
                    const savedNotes = storage.getTopicNotes(topicName);
                    if (savedNotes) {
                        DOMElements.notesView.innerHTML = savedNotes;
                    } else {
                        DOMElements.notesView.innerHTML = `<h3>Select a topic from the syllabus to see notes.</h3>`;
                    }
                },
                addChatMessage: (text, sender) => {
                    const messageDiv = document.createElement('div');
                    messageDiv.classList.add('message', sender);
                    messageDiv.textContent = text;
                    DOMElements.chatMessages.appendChild(messageDiv);
                    
                    // Force scroll to bottom with multiple methods
                    setTimeout(() => {
                        DOMElements.chatMessages.scrollTop = DOMElements.chatMessages.scrollHeight;
                        DOMElements.chatMessages.scrollIntoView({ behavior: 'smooth', block: 'end' });
                    }, 10);
                    
                    // Debug info
                    console.log('Scroll Height:', DOMElements.chatMessages.scrollHeight);
                    console.log('Client Height:', DOMElements.chatMessages.clientHeight);
                    console.log('Scroll Top:', DOMElements.chatMessages.scrollTop);
                }
            };

            const eventHandlers = {
                handleSyllabusClick: async (e) => {
                    const li = e.target.closest('li');
                    if (!li) return;
                    const topicName = li.dataset.topicName;
                    if (e.target.type === 'checkbox') {
                        await api.toggleTopic(topicName);
                        loadInitialData();
                    } else { ui.handleTopicSelection(topicName, li); }
                },
                handleGetQuestion: async () => {
                    if (!selectedTopic) return;
                    currentQuestionNumber = 1;
                    DOMElements.currentQuestionNum.textContent = currentQuestionNumber;
                    Object.assign(DOMElements.questionArea.style, { display: 'block' });
                    Object.assign(DOMElements.hintText.style, { display: 'none' });
                    Object.assign(DOMElements.resultArea.style, { display: 'none' });
                    Object.assign(DOMElements.nextQuestionBtn.style, { display: 'none' });
                    DOMElements.reviewArea.innerHTML = '';
                    DOMElements.answerInput.value = '';
                    DOMElements.questionText.textContent = 'Generating question...';
                    try {
                        const data = await api.generateQuestion(selectedTopic);
                        DOMElements.questionText.textContent = data.question;
                        DOMElements.hintText.textContent = `Hint: ${data.hint}`;
                        DOMElements.submitAnswerBtn.dataset.question = data.question;
                        DOMElements.submitAnswerBtn.disabled = false;
                    } catch (error) { DOMElements.questionText.textContent = 'Could not generate a question. Please try again.'; }
                },
                handleSubmitAnswer: async () => {
                    const question = DOMElements.submitAnswerBtn.dataset.question;
                    const answer = DOMElements.answerInput.value.trim();
                    if (!answer) return;
                    
                    DOMElements.submitAnswerBtn.disabled = true;
                    DOMElements.reviewArea.textContent = 'Reviewing...';
                    
                    try {
                        const data = await api.reviewAnswer(question, answer);
                        DOMElements.reviewArea.innerHTML = `<p>${data.review}</p>`;
                        
                        // Save submission to database
                        await api.saveSubmission(selectedTopic, question, answer, data.isCorrect);
                        
                        // Show result
                        DOMElements.resultArea.style.display = 'block';
                        DOMElements.resultArea.className = data.isCorrect ? 'correct' : 'incorrect';
                        DOMElements.resultText.textContent = data.isCorrect ? '✅ Correct!' : '❌ Incorrect, but good try!';
                        
                        // Show next question button
                        DOMElements.nextQuestionBtn.style.display = 'inline-block';
                        
                    } catch (error) { 
                        DOMElements.reviewArea.textContent = 'Error reviewing answer.'; 
                        DOMElements.submitAnswerBtn.disabled = false;
                    }
                },
                handleNextQuestion: async () => {
                    currentQuestionNumber++;
                    DOMElements.currentQuestionNum.textContent = currentQuestionNumber;
                    Object.assign(DOMElements.hintText.style, { display: 'none' });
                    Object.assign(DOMElements.resultArea.style, { display: 'none' });
                    Object.assign(DOMElements.nextQuestionBtn.style, { display: 'none' });
                    DOMElements.reviewArea.innerHTML = '';
                    DOMElements.answerInput.value = '';
                    DOMElements.questionText.textContent = 'Generating next question...';
                    
                    try {
                        const data = await api.generateQuestion(selectedTopic);
                        DOMElements.questionText.textContent = data.question;
                        DOMElements.hintText.textContent = `Hint: ${data.hint}`;
                        DOMElements.submitAnswerBtn.dataset.question = data.question;
                        DOMElements.submitAnswerBtn.disabled = false;
                    } catch (error) { DOMElements.questionText.textContent = 'Could not generate a question. Please try again.'; }
                },
                handleAiSend: async () => {
                    const query = DOMElements.aiInput.value.trim();
                    if (!query) return;
                    ui.addChatMessage(query, 'user');
                    DOMElements.aiInput.value = '';
                    try {
                        const data = await api.askAssistant(query);
                        if (data.answer) {
                            ui.addChatMessage(data.answer, 'assistant');
                        } else if (data.error) {
                            // Handle specific error messages
                            if (data.error.includes('quota') || data.error.includes('429')) {
                                ui.addChatMessage('The AI service is temporarily at capacity. Please try again in a few minutes. 🔄', 'assistant');
                            } else {
                                ui.addChatMessage(`Error: ${data.error}`, 'assistant');
                            }
                        }
                    } catch (error) { 
                        console.error('AI Assistant Error:', error);
                        ui.addChatMessage('Sorry, I encountered an error. Please try again later. 🔧', 'assistant'); 
                    }
                },
                showSubmissions: async () => {
                    try {
                        DOMElements.submissionsList.innerHTML = '<p>Loading submissions...</p>';
                        DOMElements.submissionsModal.classList.add('show');
                        
                        const data = await api.getSubmissions();
                        if (data.submissions.length === 0) {
                            DOMElements.submissionsList.innerHTML = '<p>No submissions yet. Start practicing to see your progress!</p>';
                            return;
                        }
                        
                        let submissionsHtml = '';
                        data.submissions.forEach(sub => {
                            const statusClass = sub.isCorrect ? 'correct' : 'incorrect';
                            const statusText = sub.isCorrect ? '✅ Correct' : '❌ Incorrect';
                            submissionsHtml += `
                                <div class="submission-item ${statusClass}">
                                    <div class="submission-header">
                                        <span class="submission-topic">${sub.topic}</span>
                                        <span class="submission-status ${statusClass}">${statusText}</span>
                                    </div>
                                    <div class="submission-question">Q: ${sub.question}</div>
                                    <div class="submission-answer">A: ${sub.answer}</div>
                                    <div class="submission-time">${sub.submittedAt}</div>
                                </div>
                            `;
                        });
                        DOMElements.submissionsList.innerHTML = submissionsHtml;
                    } catch (error) {
                        DOMElements.submissionsList.innerHTML = '<p>Error loading submissions. Please try again.</p>';
                    }
                }
            };

            async function loadInitialData() {
                currentUserData = await api.getUserData();
                ui.updateDashboard();
            }

            DOMElements.sidebar.addEventListener('click', eventHandlers.handleSyllabusClick);
            DOMElements.getQuestionBtn.addEventListener('click', eventHandlers.handleGetQuestion);
            DOMElements.submitAnswerBtn.addEventListener('click', eventHandlers.handleSubmitAnswer);
            DOMElements.hintBtn.addEventListener('click', () => DOMElements.hintText.style.display = 'block');
            DOMElements.hamburgerMenu.addEventListener('click', () => DOMElements.sidebar.classList.add('show'));
            DOMElements.closeBtn.addEventListener('click', () => DOMElements.sidebar.classList.remove('show'));
            DOMElements.mainContent.addEventListener('click', () => DOMElements.sidebar.classList.remove('show'));
            
            // AI Assistant popup handlers
            DOMElements.aiButton.addEventListener('click', () => DOMElements.chatPopup.classList.add('show'));
            DOMElements.chatClose.addEventListener('click', () => DOMElements.chatPopup.classList.remove('show'));
            
            // Make AI Assistant draggable
            let isDragging = false;
            let dragOffset = { x: 0, y: 0 };
            
            // Only make AI Button draggable (not the popup)
            function makeDraggable(element) {
                element.addEventListener('mousedown', (e) => {
                    // Only allow dragging on the AI button itself, not the popup
                    if (element.id === 'ai-button') {
                        isDragging = true;
                        dragOffset.x = e.clientX - element.offsetLeft;
                        dragOffset.y = e.clientY - element.offsetTop;
                        element.style.cursor = 'grabbing';
                        e.preventDefault();
                    }
                });
                
                document.addEventListener('mousemove', (e) => {
                    if (isDragging && element.style.position === 'fixed') {
                        const newX = e.clientX - dragOffset.x;
                        const newY = e.clientY - dragOffset.y;
                        
                        // Keep within viewport bounds
                        const maxX = window.innerWidth - element.offsetWidth;
                        const maxY = window.innerHeight - element.offsetHeight;
                        
                        element.style.left = Math.max(0, Math.min(newX, maxX)) + 'px';
                        element.style.top = Math.max(0, Math.min(newY, maxY)) + 'px';
                        element.style.right = 'auto';
                        element.style.bottom = 'auto';
                    }
                });
                
                document.addEventListener('mouseup', () => {
                    if (isDragging) {
                        isDragging = false;
                        element.style.cursor = 'grab';
                    }
                });
            }
            
            // Apply draggable only to AI button
            makeDraggable(DOMElements.aiButton);
            DOMElements.aiButton.style.cursor = 'grab';
            
            // Simple scroll event prevention
            DOMElements.chatPopup.addEventListener('wheel', (e) => {
                // Only stop propagation, don't prevent default scrolling within
                e.stopPropagation();
            }, { passive: true });
            
            DOMElements.aiSendBtn.addEventListener('click', eventHandlers.handleAiSend);
            DOMElements.aiInput.addEventListener('keyup', (e) => { 
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    eventHandlers.handleAiSend(); 
                }
            });
            
            DOMElements.nextQuestionBtn.addEventListener('click', eventHandlers.handleNextQuestion);
            
            // Submissions modal event listeners
            DOMElements.submissionsBtn.addEventListener('click', eventHandlers.showSubmissions);
            DOMElements.submissionsClose.addEventListener('click', () => DOMElements.submissionsModal.classList.remove('show'));

            loadInitialData();
        });
    </script>
</body>
</html>
"""

# --- App & DB Configuration ---
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("APP_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration - balanced for OAuth compatibility
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_COOKIE_SECURE'] = False  # For localhost development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db = SQLAlchemy(app)

# --- Groq AI Configuration ---
from groq import Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_KEY") or os.getenv("GROQ")
groq_client = Groq(api_key=GROQ_API_KEY)
GROQ_MODEL = os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant"

def groq_generate_text(prompt: str) -> str:
    try:
        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return completion.choices[0].message.content
    except Exception as e:
        raise e

# --- User Authentication Setup ---
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.session_protection = None  # Disable to avoid OAuth interference
login_manager.remember_cookie_duration = None  # No remember me functionality
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# --- Database Models ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    picture = db.Column(db.String(200))
    last_login = db.Column(db.Date, default=date.today)
    current_streak = db.Column(db.Integer, default=0)
    highest_streak = db.Column(db.Integer, default=0)
    login_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    
class SyllabusTopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic_name = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref=db.backref('topics', lazy=True))

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic_name = db.Column(db.String(100), nullable=False)
    question = db.Column(db.Text, nullable=False)
    user_answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('submissions', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

DSA_SYLLABUS = [
    "Big O Notation", "Arrays", "Linked Lists", "Stacks & Queues",
    "Hash Tables", "Trees, Tries & Graphs", "Heaps", "Sorting Algorithms",
    "Searching Algorithms", "Recursion", "Dynamic Programming"
]

# Authorized Users - Add email addresses of users who can access the dashboard
AUTHORIZED_USERS = None  # Set to None to allow all users

# --- Main Routes ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        return HTML_TEMPLATE_WITH_ASSETS
    return redirect(url_for('login'))

@app.route('/login')
def login():
    # Show the login page instead of immediately redirecting to OAuth
    return LOGIN_PAGE_TEMPLATE

@app.route('/oauth-login')
def oauth_login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        if user_info is None:
            resp = oauth.google.get('userinfo')
            user_info = resp.json()
        
        # Authorization: allow everyone (set AUTHORIZED_USERS to a list to restrict)
        user_email = user_info.get('email', '')
        if isinstance(AUTHORIZED_USERS, list) and AUTHORIZED_USERS and user_email not in AUTHORIZED_USERS:
            return redirect(url_for('login'))
        
        google_id = user_info['sub']  # 'sub' is the standard field for user ID in OpenID Connect
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            user = User(google_id=google_id, name=user_info['name'], email=user_info['email'],
                        picture=user_info['picture'], current_streak=1, highest_streak=1)
            db.session.add(user)
            db.session.commit()
            for topic_name in DSA_SYLLABUS:
                topic = SyllabusTopic(user_id=user.id, topic_name=topic_name)
                db.session.add(topic)
            db.session.commit()
        else:
            today = date.today()
            if user.last_login < today:
                if (today - user.last_login).days == 1: user.current_streak += 1
                else: user.current_streak = 1
                if user.current_streak > user.highest_streak: user.highest_streak = user.current_streak
                user.last_login = today
                user.login_start_time = datetime.utcnow()
                db.session.commit()
        
        login_user(user, remember=False)  # Don't remember the user session
        
        # Set session to expire when browser closes
        session.permanent = False
        
        return redirect('/')
        
    except Exception as e:
        # Handle OAuth errors (like state mismatch) by clearing session and redirecting to login
        print(f"OAuth error in authorize: {str(e)}")
        session.clear()
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # Clear all session data
    return redirect(url_for('login'))

# Clear all sessions (for testing/development)
@app.route('/clear-sessions')
def clear_sessions():
    session.clear()
    logout_user()
    return redirect(url_for('login'))

# --- API Endpoints ---
@app.route('/api/user_data')
@login_required
def user_data():
    time_spent_seconds = (datetime.utcnow() - current_user.login_start_time).total_seconds()
    user_topics = SyllabusTopic.query.filter_by(user_id=current_user.id).order_by(SyllabusTopic.id).all()
    completed_count = sum(1 for topic in user_topics if topic.completed)
    total_count = len(user_topics) if user_topics else 0
    progress_percentage = (completed_count / total_count) * 100 if total_count > 0 else 0
    return jsonify({
        'name': current_user.name, 'picture': current_user.picture,
        'time_spent_today_hours': round(time_spent_seconds / 3600, 2),
        'current_streak': current_user.current_streak, 'highest_streak': current_user.highest_streak,
        'progress_percentage': round(progress_percentage, 2),
        'syllabus': [{'name': topic.topic_name, 'completed': topic.completed} for topic in user_topics]
    })

@app.route('/api/toggle_topic', methods=['POST'])
@login_required
def toggle_topic():
    topic_name = request.json.get('topic_name')
    topic = SyllabusTopic.query.filter_by(user_id=current_user.id, topic_name=topic_name).first()
    if topic:
        topic.completed = not topic.completed
        db.session.commit()
        return jsonify({'success': True, 'completed': topic.completed})
    return jsonify({'success': False, 'error': 'Topic not found'}), 404

# --- AI API Endpoints (Groq) ---
@app.route('/api/generate_notes', methods=['POST'])
@login_required
def generate_notes():
    topic = request.json.get('topic')
    prompt = f"Generate complete, well-structured, and beginner-friendly notes on the Data Structures and Algorithms topic: '{topic}'. Use markdown for formatting, including code examples in Python."
    try:
        text = groq_generate_text(prompt)
        return jsonify({'notes': text})
    except Exception as e: 
        print(f"Error in generate_notes: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_question', methods=['POST'])
@login_required
def generate_question():
    topic = request.json.get('topic')
    import random
    question_types = [
        "concept check with examples",
        "implementation problem", 
        "time complexity analysis",
        "practical application scenario",
        "debugging challenge",
        "comparison question"
    ]
    difficulty_levels = ["beginner", "intermediate", "advanced beginner"]
    
    question_type = random.choice(question_types)
    difficulty = random.choice(difficulty_levels)
    
    prompt = f"Generate a unique {difficulty} level {question_type} about '{topic}' in Data Structures and Algorithms. Make it different from typical textbook questions. Include a practical scenario if possible. Also provide a helpful hint. Format as JSON with 'question' and 'hint' keys. Current timestamp: {datetime.utcnow().timestamp()}"
    
    try:
        # Encourage strict JSON output
        json_prompt = prompt + "\nOnly return valid JSON object like {\"question\":..., \"hint\":...} with no prose."
        text = groq_generate_text(json_prompt)
        cleaned_text = (text or "{}").strip()
        cleaned_text = cleaned_text.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(cleaned_text)
            if not isinstance(data, dict) or 'question' not in data or 'hint' not in data:
                raise ValueError('Invalid JSON keys')
            return jsonify(data)
        except Exception:
            # Fallback: extract lines or wrap response
            question_text = cleaned_text
            hint_text = "Think through definitions, examples, and complexity."
            return jsonify({"question": question_text, "hint": hint_text})
    except Exception as e:
        print(f"Error in generate_question: {str(e)}")
        return jsonify({'error': 'Failed to generate question. Please try again.'}), 500

@app.route('/api/review_answer', methods=['POST'])
@login_required
def review_answer():
    data = request.json
    prompt = f"Question: '{data.get('question')}'. User's Answer: '{data.get('answer')}'. Is the user's answer conceptually correct? Be lenient. Start your response with either 'CORRECT:' or 'INCORRECT:' followed by a brief explanation."
    try:
        review_text = groq_generate_text(prompt)
        is_correct = review_text.strip().upper().startswith('CORRECT:')
        # Clean up the response text
        clean_review = review_text.replace('CORRECT:', '').replace('INCORRECT:', '').strip()
        return jsonify({'review': clean_review, 'isCorrect': is_correct})
    except Exception as e: return jsonify({'error': str(e)}), 500

@app.route('/api/ask_assistant', methods=['POST'])
@login_required
def ask_assistant():
    query = request.json.get('query')
    prompt = f"As a helpful DSA assistant, answer the following user query concisely: '{query}'"
    try:
        text = groq_generate_text(prompt)
        return jsonify({'answer': text})
    except Exception as e: 
        error_msg = str(e)
        print(f"Error in ask_assistant: {error_msg}")
        
        # Handle specific error types
        if 'quota' in error_msg.lower() or '429' in error_msg:
            return jsonify({'error': 'API quota exceeded. Please try again in a few minutes.'}), 429
        elif 'rate limit' in error_msg.lower():
            return jsonify({'error': 'Rate limit exceeded. Please wait a moment and try again.'}), 429
        else:
            return jsonify({'error': f'AI service error: {error_msg}'}), 500

@app.route('/api/save_submission', methods=['POST'])
@login_required
def save_submission():
    try:
        data = request.json
        submission = Submission(
            user_id=current_user.id,
            topic_name=data.get('topic'),
            question=data.get('question'),
            user_answer=data.get('answer'),
            is_correct=data.get('isCorrect', False)
        )
        db.session.add(submission)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error saving submission: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_submissions', methods=['GET'])
@login_required
def get_submissions():
    try:
        submissions = Submission.query.filter_by(user_id=current_user.id).order_by(Submission.submitted_at.desc()).all()
        submissions_data = []
        for sub in submissions:
            submissions_data.append({
                'id': sub.id,
                'topic': sub.topic_name,
                'question': sub.question,
                'answer': sub.user_answer,
                'isCorrect': sub.is_correct,
                'submittedAt': sub.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify({'submissions': submissions_data})
    except Exception as e:
        print(f"Error getting submissions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test_ai')
@login_required
def test_ai():
    try:
        text = groq_generate_text("Say hello")
        return jsonify({'status': 'success', 'response': text})
    except Exception as e:
        print(f"AI API test failed: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500
        
# --- Initialize Database ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
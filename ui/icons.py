"""
SVG Icons Module - Centralized icon definitions for the Adaptive Exam Preparation AI
"""

import streamlit as st

# SVG Icons Dictionary - Professional vector icons for the interface
SVG_ICONS = {
    "graduation": '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3L1 9l4 2.18v6L12 21l7-3.82v-6l2-1.09V17h2V9L12 3zm6.82 6L12 12.72L5.18 9L12 5.28L18.82 9zM17 15.99l-5 2.73l-5-2.73v-3.72L12 15l5-2.73v3.72z"/></svg>',
    "lock": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zM12 17c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zM15.1 8H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/></svg>',
    "edit": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>',
    "user": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>',
    "shield": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11H16V19H8V11H9.2V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.4,8.7 10.4,10V11H13.6V10C13.6,8.7 12.8,8.2 12,8.2Z"/></svg>',
    "rocket": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M2.81 14.12L5.64 11.29L8.17 10.79C11.39 6.41 15.42 5.44 15.42 5.44S16.39 9.47 12.01 12.69L11.51 15.22L8.68 18.05C8.41 16.55 7.65 15.34 6.86 14.55C6.07 13.76 4.86 13 3.36 12.73L2.81 14.12Z"/></svg>',
    "target": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M12,6A6,6 0 0,0 6,12A6,6 0 0,0 12,18A6,6 0 0,0 18,12A6,6 0 0,0 12,6M12,8A4,4 0 0,1 16,12A4,4 0 0,1 12,16A4,4 0 0,1 8,12A4,4 0 0,1 12,8M12,10A2,2 0 0,0 10,12A2,2 0 0,0 12,14A2,2 0 0,0 14,12A2,2 0 0,0 12,10Z"/></svg>',
    "settings": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.22,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.22,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.68 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"/></svg>',
    "clipboard": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M19,3H14.82C14.4,1.84 13.3,1 12,1C10.7,1 9.6,1.84 9.18,3H5A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5A2,2 0 0,0 19,3M12,3A1,1 0 0,1 13,4A1,1 0 0,1 12,5A1,1 0 0,1 11,4A1,1 0 0,1 12,3"/></svg>',
    "party": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M5,4V7H10.5V19H13.5V7H19V4H5Z"/></svg>',
    "sparkles": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M16,12A2,2 0 0,1 18,10A2,2 0 0,1 20,12A2,2 0 0,1 18,14A2,2 0 0,1 16,12M10,12A2,2 0 0,1 12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12M4,12A2,2 0 0,1 6,10A2,2 0 0,1 8,12A2,2 0 0,1 6,14A2,2 0 0,1 4,12Z"/></svg>',
    "home": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z"/></svg>',
    "logout": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M16,17V14H9V10H16V7L21,12L16,17M14,2A2,2 0 0,1 16,4V6H14V4H5V20H14V18H16V20A2,2 0 0,1 14,22H5A2,2 0 0,1 3,20V4A2,2 0 0,1 5,2H14Z"/></svg>',
    "book": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M19,2L14,6.5V17.5L19,13V2M6.5,5C4.55,5 2.45,5.4 1,6.5V21.16C1,21.41 1.25,21.66 1.5,21.66C1.6,21.66 1.65,21.59 1.75,21.59C3.1,20.94 5.05,20.68 6.5,20.68C8.45,20.68 10.55,21.1 12,22C13.35,21.15 15.8,20.68 17.5,20.68C19.15,20.68 20.85,20.92 22.25,21.81C22.35,21.86 22.4,21.93 22.5,21.93C22.75,21.93 23,21.68 23,21.43V7.5C22.4,6.05 21.75,5.25 21.5,5.25C21.1,5.25 20.5,5.5 20,5.5V6.5C20,6.5 20,6.75 20,7V19.5C19.9,19.15 19.9,19 19.75,19C18.25,18.15 16.25,17.75 14.5,17.75C13.45,17.75 12.25,17.85 11.25,18.15C10.15,17.8 8.95,17.6 7.5,17.6C6.5,17.6 5.5,17.7 4.75,17.85V6.5C5.05,6.35 5.4,6.3 5.75,6.3C6.45,6.3 7.4,6.35 8.5,6.95V5.85C7.75,5.45 6.85,5.25 6.5,5.25C6.5,5.25 6.5,5 6.5,5Z"/></svg>',
    "clock": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M16.2,16.2L11,13V7H12.5V12.2L17,14.7L16.2,16.2Z"/></svg>',
    "wave": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M7,9H17V7C17,5.89 16.1,5 15,5H9C7.89,5 7,5.89 7,7V9M21,9H20V7A4,4 0 0,0 16,3H8A4,4 0 0,0 4,7V9H3A1,1 0 0,0 2,10V19A3,3 0 0,0 5,22H19A3,3 0 0,0 22,19V10A1,1 0 0,0 21,9Z"/></svg>',
    "warning": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M13,14H11V10H13M13,18H11V16H13M1,21H23L12,2L1,21Z"/></svg>',
    "error": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/></svg>',
    "success": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"/></svg>',
    "star": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12,17.27L18.18,21L16.54,13.97L22,9.24L14.81,8.62L12,2L9.19,8.62L2,9.24L7.46,13.97L5.82,21L12,17.27Z"/></svg>',
    "chart": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M22,21H2V3H4V19H6V17H10V19H12V16H16V19H18V17H22V21Z"/></svg>',
    "calendar": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M19,19H5V8H19M16,1V3H8V1H6V3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3H18V1M17,12H12V17H17V12Z"/></svg>',
    "quiz": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M19,3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3M13,13H11V11H13M13,9H11V7H13M17,13H15V11H17M17,9H15V7H17M9,13H7V11H9M9,9H7V7H9Z"/></svg>',
    "performance": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M16,6L18.29,8.29L13.41,13.17L9.41,9.17L2,16.59L3.41,18L9.41,12L13.41,16L19.71,9.71L22,12V6H16Z"/></svg>',
    "planner": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M19,19H5V8H19M16,1V3H8V1H6V3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3H18V1M17,12H12V17H17V12Z"/></svg>',
    "brain": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M21.33,12.91C21.42,14.46 20.71,15.95 19.44,16.86L20.21,18.35C20.44,18.8 20.47,19.33 20.27,19.8C20.08,20.27 19.69,20.64 19.21,20.8L18.42,21.05C18.25,21.11 18.06,21.14 17.88,21.14C17.37,21.14 16.89,20.91 16.56,20.5L14.7,18L10,16.5C8.75,16.05 7.74,15.11 7.34,13.91C6.95,12.71 7.24,11.38 8.08,10.5C7.84,9.5 8.07,8.44 8.68,7.68C9.29,6.91 10.2,6.5 11.12,6.5C11.64,6.12 12.32,5.91 13,5.91C14.22,5.91 15.35,6.5 16.08,7.5C17.24,7.88 18.16,8.82 18.47,10.04C19.47,10.47 20.15,11.43 20.15,12.5C20.15,12.64 20.13,12.78 20.1,12.91C20.8,13.07 21.26,13.71 21.33,12.91Z"/></svg>',
    "trophy": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M5,9V21H9V9H5M10,9A4,4 0 0,0 14,13A4,4 0 0,0 18,9C18,9 18,3 12,3C6,3 6,9 6,9A4,4 0 0,0 10,13A4,4 0 0,0 14,9M15,9V21H19V9H15Z"/></svg>',
    "study": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12,3L1,9L12,15L21,10.09V17H23V9M5,13.18V17.18L12,21L19,17.18V13.18L12,17L5,13.18Z"/></svg>',
    "analytics": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M22,21H2V3H4V19H6V10H10V19H12V6H16V19H18V14H22V21Z"/></svg>',
    "progress": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M13,2.05V5.08C16.39,5.57 19,8.47 19,12C19,12.9 18.82,13.75 18.5,14.54L21.12,16.07C21.68,14.83 22,13.45 22,12C22,6.82 18.05,2.55 13,2.05M12,19C8.47,19 5.57,16.39 5.08,13H2.05C2.55,18.05 6.82,22 12,22C13.45,22 14.83,21.68 16.07,21.12L14.54,18.5C13.75,18.82 12.9,19 12,19M5.08,11C5.57,7.61 8.47,5 12,5C12.9,5 13.75,5.18 14.54,5.5L16.07,2.88C14.83,2.32 13.45,2 12,2C6.82,2 2.55,5.95 2.05,11H5.08Z"/></svg>',
    "info": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/></svg>',
    "check_circle": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
    "arrow_right": '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M4,11V13H16L10.5,18.5L11.92,19.92L19.84,12L11.92,4.08L10.5,5.5L16,11H4Z"/></svg>',
    "arrow_left": '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z"/></svg>',
    "menu": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z"/></svg>',
    "close": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/></svg>',
    "download": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M5,20H19V18H5M19,9H15V3H9V9H5L12,16L19,9Z"/></svg>',
    "upload": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M9,16V10H5L12,3L19,10H15V16H9M5,20V18H19V20H5Z"/></svg>',
    "refresh": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z"/></svg>',
    "light_bulb": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12,2A7,7 0 0,0 5,9C5,11.38 6.19,13.47 8,14.74V17A1,1 0 0,0 9,18H15A1,1 0 0,0 16,17V14.74C17.81,13.47 19,11.38 19,9A7,7 0 0,0 12,2M9,21A1,1 0 0,0 10,22H14A1,1 0 0,0 15,21V20H9V21Z"/></svg>',
    "badge": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M23,12L20.56,9.22L20.9,5.54L17.29,4.72L15.4,1.54L12,3L8.6,1.54L6.71,4.72L3.1,5.53L3.44,9.21L1,12L3.44,14.78L3.1,18.47L6.71,19.29L8.6,22.47L12,21L15.4,22.46L17.29,19.28L20.9,18.46L20.56,14.78L23,12M10,17L6,13L7.41,11.59L10,14.17L16.59,7.58L18,9L10,17Z"/></svg>',
    "timer": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M15,1H9V3H15M11,14H13V8H11M19.03,7.39L20.45,5.97C20,5.46 19.55,5 19.04,4.56L17.62,6C16.07,4.74 14.12,4 12,4A9,9 0 0,0 3,13A9,9 0 0,0 12,22C17,22 21,17.97 21,13C21,10.88 20.26,8.93 19.03,7.39Z"/></svg>',
    "science": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M13,2V8H19L17,10V16A4,4 0 0,1 13,20H11A4,4 0 0,1 7,16V10L5,8H11V2H13M15,16V10.5L16.5,9H14.5V4H9.5V9H7.5L9,10.5V16A2,2 0 0,0 11,18H13A2,2 0 0,0 15,16Z"/></svg>',
    "math": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M19,3H5A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5A2,2 0 0,0 19,3M7,7H9V9H7V7M7,11H9V13H7V11M7,15H9V17H7V15M11,7H17V9H11V7M11,11H17V13H11V11M11,15H17V17H11V15Z"/></svg>',
    "history": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M13.5,8H12V13L16.28,15.54L17,14.33L13.5,12.25V8M13,3A9,9 0 0,0 4,12H1L4.96,16.03L9,12H6A7,7 0 0,1 13,5A7,7 0 0,1 20,12A7,7 0 0,1 13,19C11.07,19 9.32,18.21 8.06,16.94L6.64,18.36C8.27,20 10.5,21 13,21A9,9 0 0,0 22,12A9,9 0 0,0 13,3"/></svg>',
    "literature": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/></svg>',
    "programming": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M14.6,16.6L19.2,12L14.6,7.4L16,6L22,12L16,18L14.6,16.6M9.4,16.6L4.8,12L9.4,7.4L8,6L2,12L8,18L9.4,16.6Z"/></svg>',
    "difficulty": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12,2A3,3 0 0,1 15,5V11A3,3 0 0,1 12,14A3,3 0 0,1 9,11V5A3,3 0 0,1 12,2M19,11C19,14.53 16.39,17.44 13,17.93V21H11V17.93C7.61,17.44 5,14.53 5,11H7A5,5 0 0,0 12,16A5,5 0 0,0 17,11H19Z"/></svg>',
    "adaptive": '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4M12,6A6,6 0 0,1 18,12A6,6 0 0,1 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6M12,8A4,4 0 0,0 8,12A4,4 0 0,0 12,16A4,4 0 0,0 16,12A4,4 0 0,0 12,8Z"/></svg>'
}


def get_svg_icon(icon_name: str, size: int = 20, color: str = "currentColor") -> str:
    """
    Get SVG icon with customizable size and color.
    
    Args:
        icon_name: Name of the icon from SVG_ICONS dictionary
        size: Size of the icon in pixels (default: 20)
        color: Color of the icon (default: "currentColor")
    
    Returns:
        SVG string with specified size and color
    """
    if icon_name not in SVG_ICONS:
        return ""
    
    svg = SVG_ICONS[icon_name]
    # Replace width, height, and fill attributes
    svg = svg.replace('width="24"', f'width="{size}"')
    svg = svg.replace('width="20"', f'width="{size}"')
    svg = svg.replace('width="18"', f'width="{size}"')
    svg = svg.replace('width="16"', f'width="{size}"')
    svg = svg.replace('height="24"', f'height="{size}"')
    svg = svg.replace('height="20"', f'height="{size}"')
    svg = svg.replace('height="18"', f'height="{size}"')
    svg = svg.replace('height="16"', f'height="{size}"')
    svg = svg.replace('fill="currentColor"', f'fill="{color}"')
    
    return svg


def render_icon(icon_name: str, size: int = 20, color: str = "currentColor") -> None:
    """
    Render an SVG icon using st.markdown with HTML.
    
    Args:
        icon_name: Name of the icon from SVG_ICONS dictionary
        size: Size of the icon in pixels (default: 20)
        color: Color of the icon (default: "currentColor")
    """
    svg = get_svg_icon(icon_name, size, color)
    if svg:
        st.markdown(svg, unsafe_allow_html=True)


def icon_text(icon_name: str, text: str, size: int = 20, color: str = "currentColor", gap: str = "0.5rem") -> str:
    """
    Create HTML string with icon and text aligned.
    
    Args:
        icon_name: Name of the icon from SVG_ICONS dictionary
        text: Text to display next to the icon
        size: Size of the icon in pixels (default: 20)
        color: Color of the icon (default: "currentColor")
        gap: Gap between icon and text (default: "0.5rem")
    
    Returns:
        HTML string with icon and text
    """
    svg = get_svg_icon(icon_name, size, color)
    if svg:
        return f'<div style="display: flex; align-items: center; gap: {gap};">{svg} {text}</div>'
    return text


def icon_button(icon_name: str, text: str = "", size: int = 20, color: str = "currentColor") -> str:
    """
    Create HTML string for a button-like element with icon.
    
    Args:
        icon_name: Name of the icon from SVG_ICONS dictionary
        text: Optional text to display next to the icon
        size: Size of the icon in pixels (default: 20)
        color: Color of the icon (default: "currentColor")
    
    Returns:
        HTML string for button-like element
    """
    svg = get_svg_icon(icon_name, size, color)
    if svg:
        content = svg + (f" {text}" if text else "")
        return f'''
        <button style="
            background: none;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: {color};
            padding: 0.5rem;
            border-radius: 4px;
            transition: background-color 0.2s;
        " onmouseover="this.style.backgroundColor='rgba(255,255,255,0.1)'" 
           onmouseout="this.style.backgroundColor='transparent'">
            {content}
        </button>
        '''
    return text if text else ""


# Utility functions for common icon patterns
def success_message(message: str) -> None:
    """Display success message with check icon"""
    st.markdown(
        icon_text("success", message, color="#22c55e"),
        unsafe_allow_html=True
    )


def error_message(message: str) -> None:
    """Display error message with error icon"""
    st.markdown(
        icon_text("error", message, color="#ef4444"),
        unsafe_allow_html=True
    )


def warning_message(message: str) -> None:
    """Display warning message with warning icon"""
    st.markdown(
        icon_text("warning", message, color="#f59e0b"),
        unsafe_allow_html=True
    )


def info_message(message: str) -> None:
    """Display info message with info icon"""
    st.markdown(
        icon_text("info", message, color="#3b82f6"),
        unsafe_allow_html=True
    )

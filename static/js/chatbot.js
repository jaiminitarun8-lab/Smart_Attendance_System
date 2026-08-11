const chatToggle = document.getElementById("chatToggle");
const chatBox = document.getElementById("chatBox");

const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
const chatInput = document.getElementById("chatInput");
const chatBody = document.querySelector(".chat-body");


// =========================
// Open / Close Chat
// =========================

if (chatToggle && chatBox) {

    chatToggle.addEventListener("click", () => {

        if (chatBox.style.display === "block") {
            chatBox.style.display = "none";
        } else {
            chatBox.style.display = "block";
        }

    });

}


// =========================
// Send Button
// =========================

if (sendBtn) {
    sendBtn.addEventListener("click", sendMessage);
}


// =========================
// Enter Key
// =========================

if (chatInput) {

    chatInput.addEventListener("keypress", function (e) {

        if (e.key === "Enter") {
            e.preventDefault();
            sendMessage();
        }

    });

}


// =========================
// Send Message
// =========================

async function sendMessage() {

    const message = chatInput.value.trim();

    if (message === "") {
        return;
    }


    // =========================
    // User Message
    // =========================

    chatBody.innerHTML += `
        <div class="user-message">
            ${escapeHtml(message)}
        </div>
    `;

    chatInput.value = "";

    chatBody.scrollTop = chatBody.scrollHeight;


    try {

        // =========================
        // Backend API Call
        // =========================

        const response = await fetch("/api/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                message: message,

                user_id: localStorage.getItem("user_id"),

                role: localStorage.getItem("user_role")

            })

        });


        // =========================
        // Check HTTP Response
        // =========================

        if (!response.ok) {

            throw new Error(
                "Server returned " + response.status
            );

        }


        const data = await response.json();

        console.log("Chatbot API Response:", data);


        // =========================
        // Get Bot Reply
        // =========================

        const reply =
            data.reply ||
            data.message ||
            data.response ||
            "Sorry, mujhe abhi response nahi mila.";


        // =========================
        // Bot Message
        // =========================

        chatBody.innerHTML += `
            <div class="bot-message">
                ${escapeHtml(String(reply))}
            </div>
        `;


        // =========================
        // Voice Reply
        // =========================

        if ("speechSynthesis" in window) {

            const voice =
                new SpeechSynthesisUtterance(String(reply));

            voice.lang = "en-IN";

            voice.rate = 1;

            voice.pitch = 1;

            window.speechSynthesis.cancel();

            window.speechSynthesis.speak(voice);

        }


        // =========================
        // Scroll
        // =========================

        chatBody.scrollTop = chatBody.scrollHeight;

    }


    catch (error) {

        console.error("Chatbot Error:", error);

        chatBody.innerHTML += `
            <div class="bot-message">
                ❌ Chatbot server se response nahi mila.
            </div>
        `;

        chatBody.scrollTop = chatBody.scrollHeight;

    }

}


// =========================
// HTML Safety
// =========================

function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}


// =========================
// Voice Assistant
// =========================

if ("webkitSpeechRecognition" in window) {

    const recognition = new webkitSpeechRecognition();

    recognition.lang = "en-IN";

    recognition.continuous = false;

    recognition.interimResults = false;


    // =========================
    // Mic Button
    // =========================

    if (micBtn) {

        micBtn.addEventListener("click", () => {

            try {

                recognition.start();

            } catch (error) {

                console.log(
                    "Recognition already running."
                );

            }

        });

    }


    // =========================
    // Recognition Start
    // =========================

    recognition.onstart = () => {

        if (micBtn) {
            micBtn.innerHTML = "🎙️";
        }

    };


    // =========================
    // Recognition End
    // =========================

    recognition.onend = () => {

        if (micBtn) {
            micBtn.innerHTML = "🎤";
        }

    };


    // =========================
    // Speech Result
    // =========================

    recognition.onresult = (event) => {

        const speech =
            event.results[0][0].transcript;

        chatInput.value = speech;

        sendMessage();

    };


    // =========================
    // Recognition Error
    // =========================

    recognition.onerror = (event) => {

        console.error(
            "Speech Recognition Error:",
            event.error
        );

        if (micBtn) {
            micBtn.innerHTML = "🎤";
        }

    };

}
else {

    console.log(
        "Speech Recognition not supported in this browser."
    );

}
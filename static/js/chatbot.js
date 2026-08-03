const chatToggle = document.getElementById("chatToggle");
const chatBox = document.getElementById("chatBox");

const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
const chatInput = document.getElementById("chatInput");
const chatBody = document.querySelector(".chat-body");


// =========================
// Open / Close Chat
// =========================

chatToggle.addEventListener("click", () => {

    if (chatBox.style.display === "block") {

        chatBox.style.display = "none";

    } else {

        chatBox.style.display = "block";

    }

});


// =========================
// Send Button
// =========================

sendBtn.addEventListener("click", sendMessage);


// =========================
// Enter Key
// =========================

chatInput.addEventListener("keypress", function (e) {

    if (e.key === "Enter") {

        sendMessage();

    }

});


// =========================
// Send Message
// =========================

async function sendMessage() {

    const message = chatInput.value.trim();

    if (message === "") return;


    // User Message

    chatBody.innerHTML += `
        <div class="user-message">
            ${message}
        </div>
    `;

    chatInput.value = "";


    try {

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


        const data = await response.json();


        // Bot Message

        chatBody.innerHTML += `
            <div class="bot-message">
                ${data.reply}
            </div>
        `;


        // Voice Reply

        const voice = new SpeechSynthesisUtterance(data.reply);

        voice.lang = "en-IN";

        window.speechSynthesis.cancel();

        window.speechSynthesis.speak(voice);


        // Scroll

        chatBody.scrollTop = chatBody.scrollHeight;

    }

    catch (error) {

        console.error(error);

        chatBody.innerHTML += `
            <div class="bot-message">
                ❌ Server Error
            </div>
        `;

    }

}



// =========================
// Voice Assistant
// =========================

if ('webkitSpeechRecognition' in window) {

    const recognition = new webkitSpeechRecognition();

    recognition.lang = "en-IN";

    recognition.continuous = false;

    recognition.interimResults = false;


    micBtn.addEventListener("click", () => {

        recognition.start();

    });


    recognition.onstart = () => {

        micBtn.innerHTML = "🎙️";

    };


    recognition.onend = () => {

        micBtn.innerHTML = "🎤";

    };


    recognition.onresult = (event) => {

        const speech = event.results[0][0].transcript;

        chatInput.value = speech;

        sendMessage();

    };

}
else {

    console.log("Speech Recognition not supported.");

}
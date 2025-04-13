class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        };
        this.state = false;
        this.messages = [];
        this.queryCount = 0;
    }

    display() {
        const { openButton, chatBox, sendButton } = this.args;

        if (openButton) {
            openButton.addEventListener('click', () => this.toggleState(chatBox));
        } else {
            console.error('Chatbox button not found');
        }

        sendButton.addEventListener('click', () => this.onSendButton(chatBox));

        const node = chatBox.querySelector('input');
        node.addEventListener('keyup', ({ key }) => {
            if (key === 'Enter') {
                this.onSendButton(chatBox);
            }
        });

        const moodButton = chatBox.querySelector('#mood-prompt button');
        if (moodButton) {
            moodButton.addEventListener('click', () => this.onSubmitMood(chatBox));
        }
    }

    toggleState(chatbox) {
        this.state = !this.state;
        if (this.state) {
            chatbox.classList.add('chatbox--active');
        } else {
            chatbox.classList.remove('chatbox--active');
        }
    }

    onSendButton(chatbox) {
        const textField = chatbox.querySelector('input');
        let text1 = textField.value.trim();
        if (text1 === '') {
            return;
        }

        let msg1 = { name: 'User', message: text1 };
        this.messages.push(msg1);
        this.updateChatText(chatbox);

        fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(r => r.json())
            .then(r => {
                let msg2 = { name: 'Zara', message: r.answer };
                this.messages.push(msg2);
                this.queryCount = r.query_count;
                this.updateChatText(chatbox);
                textField.value = '';

                if (this.queryCount % 5 === 0) { // Changed from % 10 to % 5
                    const moodPrompt = chatbox.querySelector('#mood-prompt');
                    if (moodPrompt) {
                        moodPrompt.style.display = 'block';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.messages.push({ name: 'Zara', message: 'Sorry, something went wrong.' });
                this.updateChatText(chatbox);
                textField.value = '';
            });
    }

    onSubmitMood(chatbox) {
        const moodField = chatbox.querySelector('#mood-input');
        const mood = parseInt(moodField.value);
        if (mood < 1 || mood > 10 || isNaN(mood)) {
            alert('Please enter a mood between 1 and 10.');
            return;
        }

        fetch('http://127.0.0.1:5000/mood', {
            method: 'POST',
            body: JSON.stringify({ mood }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(r => r.json())
            .then(r => {
                this.messages.push({ name: 'Zara', message: 'Thank you for sharing your mood!' });
                this.updateChatText(chatbox);
                const moodPrompt = chatbox.querySelector('#mood-prompt');
                if (moodPrompt) {
                    moodPrompt.style.display = 'none';
                }
                moodField.value = '';
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error submitting mood.');
            });
    }

    updateChatText(chatbox) {
        let html = '';
        this.messages.slice().reverse().forEach(function (item) {
            if (item.name === 'Zara') {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>';
            } else {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>';
            }
        });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
        chatmessage.scrollTop = chatmessage.scrollHeight;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const chatbox = new Chatbox();
    chatbox.display();
});
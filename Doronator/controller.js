let midiOut = null;

// 1. חיבור ל-API
if (navigator.requestMIDIAccess) {
    navigator.requestMIDIAccess().then(onSuccess, onFailure);
} else {
    document.getElementById('status').innerText = "הדפדפן שלך לא תומך ב-MIDI";
}

function onSuccess(midiAccess) {
    const outputs = Array.from(midiAccess.outputs.values());
    if (outputs.length > 0) {
        midiOut = outputs[0]; // בוחר את המכשיר הראשון ברשימה
        document.getElementById('status').innerText = `מחובר ל: ${midiOut.name}`;
    } else {
        document.getElementById('status').innerText = "לא נמצאו מכשירי פלט MIDI";
    }
}

function onFailure() {
    document.getElementById('status').innerText = "נכשל בגישה ל-MIDI";
}

// 2. פונקציית לחיצה (Note On)
function playNote(note) {
    if (!midiOut) return;
    
    // 0x90 = Note On ערוץ 1
    // note = מספר התו (למשל 60)
    // 0x7f = עוצמה מקסימלית (127)
    midiOut.send([0x90, note, 0x7f]);
}

// 3. פונקציית שחרור (Note Off)
function stopNote(note) {
    if (!midiOut) return;
    
    // 0x80 = Note Off ערוץ 1
    midiOut.send([0x80, note, 0x00]);
}
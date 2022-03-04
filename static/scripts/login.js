// the Elemets
let login
let signup
let loginButton
let signButton

window.onload = () => {

    // Load those buttons after the documents load
    login = document.getElementById("login")
    signup = document.getElementById("signup")

    loginButton = document.getElementById("login-btn")
    signButton = document.getElementById("sign-btn")

}

const signUp = () => {

    login.style.display = "none"
    signup.style.display = "block"
}

const logIn = () => {

    signup.style.display = "none"
    login.style.display = "block"
}


const checkLength = (element) => {
    
    // Check the element length and alert the user
    if (element.value.trim().length < 8) {

        // Disable the buttons and show warning
        loginButton.disabled = true
        signButton.disabled = true
        window.alert("Password must be atleast 8 letters")

    } else {

        // Enable those buttons
        loginButton.disabled = false
        signButton.disabled = false
    }
}

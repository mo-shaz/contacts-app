// the Elemets
let login
let signup

window.onload = () => {

    login = document.getElementById("login")
    signup = document.getElementById("signup")

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
        window.alert("Password must be atleast 8 letters")
    }
}

import React, { Component } from 'react';

class SignIn extends Component {
    constructor(props){
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleSubmit(event){
        event.preventDefault();
        this.props.onLogIn(event);
    }
    render(){
        return(
            <div >
                <form onSubmit={this.handleSubmit}>
                    Email:
                        <input type="text" name="logemail"/> <br/>
                    Password:
                        <input type="password" name="logpassword"/> <br/>
                    <button type="submit" value="Submit"> Submit </button>
                </form>
            </div>
        )
    }
}

export default SignIn;

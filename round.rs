
fn main() {
    round_up();
    round_down();
}

fn round_up() {
    let n = -0.5_f64;
let y = n.ceil();

println!("The ceiling of {} is {}", n, y);

if y.is_sign_negative() {
    println!("The result is negative");
    if y == 0.0 {
        println!("The result is equal to positive zero");
    }
    else if y == -0.0 {
        println!("The result is equal to negative zero");
    }
    else if y < 0.0 {
        println!("The result is less than zero");
    }
    else if y > 0.0 {
        println!("The result is greater than zero");
    }
     
} else {
    println!("The result is positive");
}
}


fn round_down() {
    let n = 0.5_f64;
let y = n.floor();
println!("The floor of {} is {}", n, y);
if y.is_sign_negative() {
    println!("The result is negative"); 
} else {
    println!("The result is positive");
}

}

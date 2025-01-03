def calculate_area(radius):
    pi = 3.14
    area = pi * radius * radius
    return area

def main():
    radius = input("Enter the radius: ")
    area = calculate_area(radius)
    print("The area is: " + area)

    if area > 0:
        print("The area is positive.")
    else:
        print("The area is negative.")

    radius = input("Enter another radius: ")
    area = calculate_area(radius)
    print("Area again: " + area)

    radius = input("Enter a third radius: ")
    if radius < 0:
        print("Radius cannot be negative!")
    else:
        area = calculate_area(radius)
        print("Area for third radius: " + area)

    print("Done!")

main()

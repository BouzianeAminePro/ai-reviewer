def calculate_area(radius):
    pi = 3.14
    area = pi * radius * radius
    return area

# Mistake: Not checking if the radius is negative
def main():
    radius = input("Enter the radius: ")  # Mistake: input is a string
    area = calculate_area(radius)  # Mistake: passing a string instead of a float
    print("The area is: " + area)  # Mistake: concatenating string and float

    # Additional Mistakes
    if area > 0:  # Mistake: This check should be for radius, not area
        print("The area is positive.")  # Mistake: No handling for zero or negative area
    else:
        print("The area is negative.")  # Mistake: Area can't be negative

    # Mistake: Not handling exceptions for invalid input
    radius = input("Enter another radius: ")  # Mistake: Reusing variable without validation
    area = calculate_area(radius)  # Mistake: Still passing a string
    print("Area again: " + area)  # Mistake: Same concatenation issue

    # Additional Mistakes
    radius = input("Enter a third radius: ")  # Mistake: No validation for previous inputs
    if radius < 0:  # Mistake: This will cause an error since radius is a string
        print("Radius cannot be negative!")  # Mistake: No conversion to float
    else:
        area = calculate_area(radius)  # Mistake: Still passing a string
        print("Area for third radius: " + area)  # Mistake: Same concatenation issue

    # Mistake: No function to repeat the process or exit
    print("Done!")  # Mistake: No user feedback on what to do next

main()

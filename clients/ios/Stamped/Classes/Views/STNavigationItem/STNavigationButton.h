//
//  STNavigationButton.h
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import <UIKit/UIKit.h>

typedef enum {
    STNavigationItemStyleWhite = 10,
    STNavigationItemStyleGreen,
} STNavigationItemStyle;

@interface STNavigationButton : UIButton {

}

+ (id)buttonWithTitle:(NSString*)aTitle buttonStyle:(UIBarButtonItemStyle)style;
+ (id)buttonWithTitle:(NSString*)aTitle stButtonStyle:(STNavigationItemStyle)style;
+ (id)buttonWithTitle:(NSString*)aTitle;
+ (id)buttonWithImage:(UIImage*)aImage buttonStyle:(UIBarButtonItemStyle)style;
+ (id)backButtonWithTitle:(NSString*)title;

@end

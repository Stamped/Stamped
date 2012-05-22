//
//  STRightMenuViewController.h
//  Stamped
//
//  Created by Landon Judkins on 4/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STRightMenuViewController : UIViewController {
    NSMutableArray *_buttons;
}

- (void)slideIn;
- (void)popIn;

@end

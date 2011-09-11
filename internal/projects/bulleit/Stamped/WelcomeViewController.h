//
//  WelcomeViewController.h
//  Stamped
//
//  Created by Robert Sesek on 9/10/11.
//  Copyright 2011 Stamped. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface WelcomeViewController : UIViewController<UIScrollViewDelegate>

@property (nonatomic, retain) IBOutlet UIView* contentView;
@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UIPageControl* pageControl;

- (IBAction)findfromContacts:(id)sender;
- (IBAction)findFromTwitter:(id)sender;

- (IBAction)pageViewChanged:(id)sender;

@end

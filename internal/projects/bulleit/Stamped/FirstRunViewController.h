//
//  FirstRunViewController.h
//  Stamped
//
//  Created by Jake Zien on 9/4/11.
//  Copyright Stamped, Inc. All rights reserved.
//

#import <QuartzCore/QuartzCore.h>
#import <UIKit/UIKit.h>

@interface FirstRunViewController : UIViewController <UIScrollViewDelegate>

@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UIView* bottomView;
@property (nonatomic, retain) IBOutlet UIView* animView;

@end

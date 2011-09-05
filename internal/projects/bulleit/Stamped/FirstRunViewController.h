//
//  LearnMoreViewController.h
//  Stamped
//
//  Created by Jake Zien on 9/4/11.
//  Copyright 2011 RISD. All rights reserved.
//

#import <QuartzCore/QuartzCore.h>
#import <UIKit/UIKit.h>

@interface LearnMoreViewController : UIViewController <UIScrollViewDelegate>
{
  UIScrollView* scrollView;
}


@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UIView* bottomView;
@property (nonatomic, retain) IBOutlet UIView* animView;

- (void)setupBottomView;
- (UIImage*) maskImage:(UIImage *)image
              withMask:(UIImage *)maskImage;
- (void)setupSlide:(UIImageView*)imageView;

@end

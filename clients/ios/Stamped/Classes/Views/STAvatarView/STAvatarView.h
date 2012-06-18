//
//  STAvatarView.h
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import <UIKit/UIKit.h>

@class STTextCalloutView;
@protocol STAvatarViewDelegate;
@interface STAvatarView : UIControl {
    UIView *highlightView;
    STTextCalloutView *_calloutView;
}

@property(nonatomic,retain) NSURL *imageURL;
@property(nonatomic,retain,readonly) UIImageView *imageView;
@property(nonatomic,retain,readonly) UIView *backgroundView;
@property(nonatomic,assign) id <STAvatarViewDelegate> delegate;
@property(nonatomic,copy) NSString *calloutTitle;

- (void)setDefault;

@end

@protocol STAvatarViewDelegate
- (void)stAvatarViewTapped:(STAvatarView*)view;
@end
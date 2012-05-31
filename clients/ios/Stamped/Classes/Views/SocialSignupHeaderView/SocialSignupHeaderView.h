//
//  SocialSignupHeaderView.h
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import <UIKit/UIKit.h>

@class STAvatarView;
@interface SocialSignupHeaderView : UIView {
    UIImageView *_stampView;
}

@property(nonatomic,retain,readonly) STAvatarView *imageView;
@property(nonatomic,retain,readonly) UILabel *titleLabel;
@property(nonatomic,retain,readonly) UILabel *subTitleLabel;
@property(nonatomic,retain,readonly) UILabel *detailLabel;

- (void)setStampColors:(NSArray*)colors;

@end

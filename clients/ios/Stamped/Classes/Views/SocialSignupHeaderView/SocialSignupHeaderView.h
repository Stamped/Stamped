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
    STAvatarView *_userImageView;
    UIImageView *_stampView;
    UILabel *_nameLabel;
    UILabel *_locationLabel;
    UILabel *_bioLabel;
}

- (void)setStampColors:(NSArray*)colors;

@end

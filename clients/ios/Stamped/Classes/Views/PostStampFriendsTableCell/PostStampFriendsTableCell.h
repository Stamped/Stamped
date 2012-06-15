//
//  PostStampFriendsTableCell.h
//  Stamped
//
//  Created by Devin Doty on 6/15/12.
//
//

#import <UIKit/UIKit.h>

@interface PostStampFriendsTableCell : UITableViewCell {
    CATextLayer *_titleLayer;
    UIView *_borderView;
    UIImageView *_shadowView;
    NSArray *_userViews;
}

- (void)setupWithStampedBy:(id<STStampedBy>)stampedBy andStamp:(id<STStamp>)stamp;
- (void)showShadow:(BOOL)show;

@end

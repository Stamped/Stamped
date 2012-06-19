//
//  PostStampFriendsTableCell.h
//  Stamped
//
//  Created by Devin Doty on 6/15/12.
//
//

#import <UIKit/UIKit.h>

@protocol PostStampFriendsTableCellDelegate;
@interface PostStampFriendsTableCell : UITableViewCell {
    CATextLayer *_titleLayer;
    UIView *_borderView;
    UIImageView *_shadowView;
    NSArray *_userViews;
}

@property(nonatomic,assign) id <PostStampFriendsTableCellDelegate> delegate;

- (void)setupWithStampedBy:(id<STStampedBy>)stampedBy andStamp:(id<STStamp>)stamp;
- (void)showShadow:(BOOL)show;

@end
@protocol PostStampFriendsTableCellDelegate
- (void)postStampFriendTableCell:(PostStampFriendsTableCell*)cell selectedStamp:(id<STStamp>)stamp;
@end
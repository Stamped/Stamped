//
//  FriendStatusButton.h
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import <UIKit/UIKit.h>

typedef enum {
    FriendStatusNotFollowing = 0,
    FriendStatusFollowing,
    FriendStatusRequestSent,
    FriendStatusInvite,
    FriendStatusInviteSent,
} FriendStatus;

@interface FriendStatusButton : UIButton {
    UIActivityIndicatorView *_activityView;
}

@property(nonatomic,assign) FriendStatus status;
@property(nonatomic,assign) BOOL loading;

@end

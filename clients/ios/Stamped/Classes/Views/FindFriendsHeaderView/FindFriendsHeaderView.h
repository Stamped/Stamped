//
//  FindFriendsHeaderView.h
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import <UIKit/UIKit.h>

typedef enum {
    FindFriendsSelectionTypeContacts = 0,
    FindFriendsSelectionTypeFacebook,
    FindFriendsSelectionTypeTwitter,
} FindFriendsSelectionType;

@protocol FindFriendsHeaderViewDelegate;
@interface FindFriendsHeaderView : UIView
@property(nonatomic,assign) id delegate;
@end
@protocol FindFriendsHeaderViewDelegate
- (void)findFriendsHeaderView:(FindFriendsHeaderView*)view selectedType:(FindFriendsSelectionType)type;
@end
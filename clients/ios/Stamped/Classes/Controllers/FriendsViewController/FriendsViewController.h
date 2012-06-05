//
//  FriendsViewController.h
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import <UIKit/UIKit.h>
#import "STRestViewController.h"
#import "Friends.h"

@interface FriendsViewController : STRestViewController <UITableViewDataSource, UITableViewDelegate> {
    BOOL _performingAuth;
}

- (id)initWithType:(FriendsRequestType)type;


@end

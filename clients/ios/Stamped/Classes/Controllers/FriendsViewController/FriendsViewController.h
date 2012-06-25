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

@interface FriendsViewController : STRestViewController <UITableViewDataSource, UITableViewDelegate, STRestController> {
    BOOL _performingAuth;
}

- (id)initWithType:(FriendsRequestType)type;

- (id)initWithQuery:(NSString*)query;


@end

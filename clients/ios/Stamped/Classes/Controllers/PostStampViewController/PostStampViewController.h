//
//  PostStampViewController.h
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import <UIKit/UIKit.h>

@class STStampContainerView;
@interface PostStampViewController : UITableViewController {
    STStampContainerView *_tvContainer;
}

- (id)initWithStamp:(id<STStamp>)stamp;

@end

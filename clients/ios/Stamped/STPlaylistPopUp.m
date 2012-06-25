//
//  STPlaylistPopUp.m
//  Stamped
//
//  Created by Landon Judkins on 4/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STPlaylistPopUp.h"
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"
#import "Util.h"
#import "STSimplePlaylistItem.h"
#import "STSimpleAction.h"

static CGFloat _rowHeight = 44;

@interface STPlaylistPopUp ()

@end

@implementation STPlaylistPopUp

@synthesize playlistItems = _playlistItems;

- (id)initWithSource:(id<STSource>)source action:(NSString*)action andContext:(STActionContext*)context
{
  self = [super init];
  if (self) {
    self.backgroundColor = [UIColor whiteColor];
    if (context.entityDetail) {
      CGFloat height = 40;
      CGFloat titleX = 100;
      if (context.entityDetail.images && context.entityDetail.images.count > 0) {
        id<STImageList> imageList = [context.entityDetail.images objectAtIndex:0];
        if (imageList.sizes.count > 0) {
          id<STImage> image = [imageList.sizes objectAtIndex:0];
          UIView* imageView = [Util imageViewWithURL:[NSURL URLWithString:image.url] andFrame:CGRectNull];
          CGFloat imagePadding = 10;
          [Util reframeView:imageView withDeltas:CGRectMake(imagePadding, imagePadding, 0, 0)];
          height = MAX(CGRectGetMaxY(imageView.frame) + imagePadding, height);
          titleX = MAX(CGRectGetMaxX(imageView.frame) + imagePadding, titleX);
          [self.header addSubview:imageView];
        }
      }
      UIView* titleView = [Util viewWithText:context.entityDetail.title
                                        font:[UIFont stampedTitleFont]
                                       color:[UIColor stampedDarkGrayColor]
                                        mode:UILineBreakModeTailTruncation
                                  andMaxSize:CGSizeMake(self.frame.size.width - (titleX + 10), height)];
      titleView.frame = [Util centeredAndBounded:titleView.frame.size inFrame:CGRectMake(titleX, 0, titleView.frame.size.width, height)];
      [self.header addSubview:titleView];
      [self childView:self.header shouldChangeHeightBy:height overDuration:0];
      
      NSInteger row = 0;
      if (context.entityDetail.playlist.data.count > 0 && source.sourceID) {
        NSMutableArray<STPlaylistItem>* array = [NSMutableArray array];
        for (NSInteger i = 0; i < context.entityDetail.playlist.data.count; i++) {
          id<STPlaylistItem> item = [context.entityDetail.playlist.data objectAtIndex:i];
          NSString* itemID = [self getItemId:item];
          if (itemID) {
            [array addObject:item];
            if ([itemID isEqualToString:source.sourceID]) {
              row = i;
            }
          }
        }
        _playlistItems = [array retain];
      }
      else {
        STSimplePlaylistItem* item = [[[STSimplePlaylistItem alloc] init] autorelease];
        item.name = context.entityDetail.title;
        item.action = [STSimpleAction actionWithType:action andSource:source];
        _playlistItems = [[NSArray arrayWithObject:item] retain];
      }
      
      self.table.backgroundColor = [UIColor colorWithWhite:1 alpha:1];
      self.footer.backgroundColor = [UIColor colorWithWhite:0 alpha:.5];
      self.header.backgroundColor = [UIColor colorWithWhite:.95 alpha:1];
      //[self childView:self.footer shouldChangeHeightBy:50 overDuration:0];
      if (_playlistItems.count > 0) {
        CGFloat tableHeight = _playlistItems.count * _rowHeight;
        if (tableHeight < self.table.frame.size.height) {
          [self childView:self.table shouldChangeHeightBy:tableHeight-self.table.frame.size.height overDuration:0];
        }
          //self.table.editing = YES;
        self.table.rowHeight = _rowHeight;
        [self.table reloadData];
        [self.table selectRowAtIndexPath:[NSIndexPath indexPathForRow:row inSection:0] animated:NO scrollPosition:UITableViewScrollPositionTop];
        [self tableView:self.table didSelectRowAtIndexPath:[NSIndexPath indexPathForRow:row inSection:0]];
      }
    }
    else {
      NSAssert(NO, @"no support for entity-less playback");
    }
  }
  return self;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  assert(section == 0);
  return [self.playlistItems count];
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  return 1;
}

- (void)test:(id)notImportant {
    self.table.editing = !self.table.editing;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  id<STPlaylistItem> item = [self.playlistItems objectAtIndex:indexPath.row];
  UITableViewCell* cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleValue1 reuseIdentifier:@"track"] autorelease];
  
    //UISwipeGestureRecognizer* recognizer = [[[UISwipeGestureRecognizer alloc] initWithTarget:self action:@selector(test:)] autorelease];
    //recognizer.direction = UISwipeGestureRecognizerDirectionRight;
    //cell.showsReorderControl = YES;
    //[cell addGestureRecognizer:recognizer];
    cell.textLabel.text = item.name ? item.name : @"?";
    return cell;
}

- (BOOL)tableView:(UITableView *)tableview canMoveRowAtIndexPath:(NSIndexPath *)indexPath {
	return NO;	
}

- (void)tableView:(UITableView *)tableView moveRowAtIndexPath:(NSIndexPath *)fromIndexPath toIndexPath:(NSIndexPath *)toIndexPath {
	
}
- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  
}

- (NSString*)getItemId:(id<STPlaylistItem>)item {
  return nil;
}

@end

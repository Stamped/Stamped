//
//  STSettingsViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/7/12.
//
//

#import "STSettingsViewController.h"
#import "SettingsTableCell.h"

@interface STSettingsViewController ()

@end

@implementation STSettingsViewController

- (id)init {
    
    if ((self = [super initWithStyle:UITableViewStyleGrouped])) {
        self.title = NSLocalizedString(@"Settings", @"Settings");
        
        NSArray *you = [NSArray arrayWithObjects:@"Edit profile", @"Connected accounts", @"Notifications", nil];
        NSArray *stamped = [NSArray arrayWithObjects:@"About us", @"Frequently asked questions", @"Legal", nil];
        NSArray *feedback = [NSArray arrayWithObject:@"Send feedback"];
        NSArray *signOut = [NSArray arrayWithObject:@"Sign out"];

        _dataSource = [[NSArray arrayWithObjects:you, stamped, feedback, signOut, nil] retain];
        _sectionViews = [[NSMutableArray alloc] initWithCapacity:[_dataSource count]];
        
        for (NSInteger i = 0; i < [_dataSource count]; i++) {
            [_sectionViews addObject:[NSNull null]];
        }
        
    }
    return self;
    
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.view.bounds];
    background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    [background setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
        drawGradient([UIColor colorWithRed:0.961f green:0.961f blue:0.957f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
    }];
    self.tableView.backgroundView = background;
    [background release];
    
    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
    self.tableView.rowHeight = 40.0f;
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
}

- (void)dealloc {
    
    [_sectionViews release], _sectionViews=nil;
    [_dataSource release], _dataSource=nil;
    [super dealloc];
}


#pragma mark - UITableViewDataSource

- (void)setupSectionAtIndex:(NSInteger)index {
    
    UIView *view = [_sectionViews objectAtIndex:index];
    
    if ([view isEqual:[NSNull null]]) {
        
        STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:CGRectMake(12.0f, 0.0f, self.tableView.bounds.size.width-24.0f, 0.0f)];
        background.userInteractionEnabled = NO;
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        background.backgroundColor = [UIColor clearColor];
        [background setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
            
            CGFloat inset = 6.0f;
            CGFloat corner = 2.0f;
            
            UIColor *topColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:0.6f];
            UIColor *bottomColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:0.8f];
            
            CGPathRef path = [UIBezierPath bezierPathWithRoundedRect:CGRectInset(rect, inset, 2) cornerRadius:corner].CGPath;

            // drop shadow
            CGContextSaveGState(ctx);
            CGContextSetFillColorWithColor(ctx, [UIColor whiteColor].CGColor);
            CGContextSetShadowWithColor(ctx, CGSizeMake(0.0f, 1.0f), 2.0f, [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.05].CGColor);
            CGContextAddPath(ctx, path);
            CGContextFillPath(ctx);
            CGContextAddPath(ctx, path);
            CGContextClip(ctx);
            CGContextClearRect(ctx, rect);
            CGContextRestoreGState(ctx);
            
            // gradient fill
            CGContextSaveGState(ctx);
            CGContextAddPath(ctx, path);
            CGContextClip(ctx);
            drawGradient(topColor.CGColor, bottomColor.CGColor, ctx);
            
            // inner shadow
            CGFloat originY = 2.0f;
            CGFloat originX = inset;
            CGContextSetStrokeColorWithColor(ctx, [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor);
            CGContextMoveToPoint(ctx, originX, originY + corner);
            CGContextAddQuadCurveToPoint(ctx, originX, originY, originX + corner, originY);
            CGContextAddLineToPoint(ctx, rect.size.width-(originX+corner), originY);
            CGContextAddQuadCurveToPoint(ctx, rect.size.width-originX, originY, rect.size.width-originX, originY + corner);
            CGContextStrokePath(ctx);
            CGContextRestoreGState(ctx);
            
            // gradient stroke
            topColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:0.6f];
            bottomColor = [UIColor colorWithRed:0.8f green:0.8f blue:0.8f alpha:0.8f];
            CGContextAddPath(ctx, path);
            CGContextReplacePathWithStrokedPath(ctx);
            CGContextClip(ctx);
            drawGradient(topColor.CGColor, bottomColor.CGColor, ctx);
            
        }];
        
        [self.tableView insertSubview:background atIndex:0];
        background.clipsToBounds = NO;
        [_sectionViews replaceObjectAtIndex:index withObject:background];
        [background release];
        view = background;
        
    }
    
    CGRect frame = view.frame;
    NSArray *section = [_dataSource objectAtIndex:index];
    frame.size.height = (40.0f * [section count]) + 4.0f;
    frame.origin.y = [self.tableView rectForSection:index].origin.y;
  
    if (index < 2) {
        frame.origin.y += 29.0f;
    } else {
        frame.origin.y += 8.0f;
    }
    
    view.frame = frame;
    [self.tableView sendSubviewToBack:view];
    
}

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
    return [_dataSource count];
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    NSArray *aSection = [_dataSource objectAtIndex:section];
    return [aSection count];    
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (indexPath.row == 0) {
        [self setupSectionAtIndex:indexPath.section];
    }
    
    static NSString *CellIdentifier = @"CellIdentifier";
    
    SettingsTableCell *cell = (SettingsTableCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell =[[[SettingsTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }

    NSArray *aSection = [_dataSource objectAtIndex:indexPath.section];
    
    cell.titleLabel.text = [aSection objectAtIndex:indexPath.row];
    if ([aSection count] > 1) {
        [cell setFirst:indexPath.row == 0 last:(indexPath.row == [aSection count]-1)];
    } else {
        [cell setFirst:YES last:YES];
    }

    cell.layer.zPosition = 10;
    return cell;
    
}

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
    if (section > 1) {
        return 0.0f;
    }
    return 30.0f;
}

- (UIView*)labelWithTitle:(NSString*)title {
    
    UIView *view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 30.0f)];
    
    UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
    label.backgroundColor = [UIColor clearColor];
    label.textColor = [UIColor colorWithRed:0.600f green:0.600f blue:0.600f alpha:1.0f];
    label.shadowColor = [UIColor whiteColor];
    label.shadowOffset = CGSizeMake(0.0f, 1.0f);
    label.font = [UIFont boldSystemFontOfSize:12];
    label.text = title;
    
    [label sizeToFit];
    CGRect frame = label.frame;
    frame.origin.x = 15.0f;
    frame.origin.y = floorf((view.bounds.size.height-frame.size.height)/2);
    label.frame = frame;
    [view addSubview:label];
    [label release];

    return [view autorelease];
    
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
    if (section > 1) {
        return nil;
    }

    return [self labelWithTitle:section==0 ? @"You" : @"Stamped"];
    
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (indexPath.section == 0) {
        
        // you
        
        [tableView deselectRowAtIndexPath:indexPath animated:YES];

    } else if (indexPath.section == 1) {
        
        // stamped
        
        [tableView deselectRowAtIndexPath:indexPath animated:YES];

        
    } else if (indexPath.section == 2) {
        
        // feedback
        
        [tableView deselectRowAtIndexPath:indexPath animated:YES];

        
    } else if (indexPath.section == 3) {
        
        // sign out
        
        UIActionSheet *actionSheet = [[UIActionSheet alloc] initWithTitle:@"Are you sure you want to sign out?" delegate:(id<UIActionSheetDelegate>)self cancelButtonTitle:@"Cancel" destructiveButtonTitle:@"Sign out" otherButtonTitles:nil];
        actionSheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
        [actionSheet showInView:self.view];
        [actionSheet release];
        
    }
    
    
    
}


#pragma mark - UIActionSheetDelegate

- (void)actionSheet:(UIActionSheet *)actionSheet clickedButtonAtIndex:(NSInteger)buttonIndex {
    
    [self.tableView deselectRowAtIndexPath:self.tableView.indexPathForSelectedRow animated:YES];
    
}


@end
